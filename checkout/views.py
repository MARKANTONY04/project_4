# checkout/views.py
import json
from decimal import Decimal
from django.conf import settings
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from bag.views import _normalize_session_bag, _get_product  # reuse helpers to read session bag
from bag.models import SavedBagItem
from .models import Order, OrderLineItem


def _get_bag_items_for_checkout(request):
    """
    Return a list of dicts: {product, item_type, id, quantity, unit_price}
    Works for logged-in (SavedBagItem) and guest (session).
    """
    items = []

    if request.user.is_authenticated:
        saved = SavedBagItem.objects.filter(user=request.user)
        for s in saved:
            product = _get_product(s.item_type, s.item_id)
            if not product:
                continue
            items.append({
                'product': product,
                'type': s.item_type,
                'id': s.item_id,
                'quantity': s.quantity,
                'unit_price': Decimal(getattr(product, 'price', 0)),
                'display_name': getattr(product, 'name', getattr(product, 'title', str(product)))
            })
    else:
        session_bag = _normalize_session_bag(request.session.get('bag', {}))
        for key, val in session_bag.items():
            item_type = val['type']
            item_id = val['id']
            quantity = val['quantity']
            product = _get_product(item_type, item_id)
            if not product:
                continue
            items.append({
                'product': product,
                'type': item_type,
                'id': item_id,
                'quantity': quantity,
                'unit_price': Decimal(getattr(product, 'price', 0)),
                'display_name': getattr(product, 'name', getattr(product, 'title', str(product)))
            })
    return items


@require_POST
def create_checkout_session(request):
    """
    Create a Stripe Checkout Session and return session id as JSON.
    Expects POST with optional contact info (or we can pull from user).
    """
    data = request.POST
    # optionally collect customer name/email etc. For brevity, we'll let Stripe collect email on checkout.
    line_items = []
    bag_items = _get_bag_items_for_checkout(request)
    if not bag_items:
        return JsonResponse({'error': 'Your bag is empty.'}, status=400)

    for it in bag_items:
        # Stripe wants amount in pence/cents (integer)
        unit_amount = int((it['unit_price'] * 100).quantize(Decimal('1')))
        if unit_amount < 0:
            unit_amount = 0
        line_items.append({
            'price_data': {
                'currency': 'gbp',
                'product_data': {
                    'name': it['display_name'],
                },
                'unit_amount': unit_amount,
            },
            'quantity': it['quantity'],
        })

    DOMAIN = request.build_absolute_uri('/')[:-1]  # root domain

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=DOMAIN + reverse('checkout:success') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=DOMAIN + reverse('checkout:cancel'),
            # optionally: pass metadata to later reconcile in webhook
            metadata={
                'user_id': request.user.id if request.user.is_authenticated else '',
                # you can also add a small JSON payload with items, but keep metadata small
            },
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    # client will redirect to session.url or receive session id to use stripe.redirectToCheckout
    return JsonResponse({'id': session.id, 'url': session.url})


def success(request):
    # optionally show order info
    session_id = request.GET.get('session_id')
    return render(request, 'checkout/success.html', {'session_id': session_id})


def cancel(request):
    return render(request, 'checkout/cancel.html')


# webhook.py for views to handle Stripe webhooks
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return HttpResponseBadRequest()  # invalid payload
    except stripe.error.SignatureVerificationError as e:
        return HttpResponseBadRequest()  # invalid signature

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_successful_checkout_session(session)

    # optionally handle payment_intent.succeeded etc.
    return HttpResponse(status=200)


def handle_successful_checkout_session(session):
    """
    Create Order and OrderLineItems from the session object.
    We need to map session to our bag items.
    We'll prefer to reconstruct items from our DB/session if possible.
    """
    # session.id, session.payment_intent, session.customer_details.email etc.
    # Best practice: use session.client_reference_id or metadata to map a user or a bag snapshot.
    sid = session.get('id')
    payment_intent = session.get('payment_intent')
    cust_email = session.get('customer_details', {}).get('email')
    # If you stored user_id in metadata:
    user_id = session.get('metadata', {}).get('user_id') or None

    # Attempt to load a user if user_id present (optional)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = None
    if user_id:
        try:
            user = User.objects.get(pk=int(user_id))
        except Exception:
            user = None

    # Reconstruct line items by other means:
    # Option A: fetch the Checkout Session line items from Stripe (safer)
    try:
        stripe_line_items = stripe.checkout.Session.list_line_items(sid, limit=100)
    except Exception:
        stripe_line_items = []

    # Create Order
    order = Order.objects.create(
        user=user,
        stripe_payment_intent=payment_intent or '',
        stripe_session_id=sid,
        full_name=session.get('customer_details', {}).get('name', '') or cust_email or 'Guest',
        email=cust_email or '',
        paid=True,
    )

    # For each stripe line item, try to match to our services products by name or fallback generic
    for li in getattr(stripe_line_items, 'data', []):
        name = li.get('description') or li.get('price', {}).get('product') or li.get('price', {}).get('nickname') or li.get('price', {}).get('currency')
        quantity = li.get('quantity', 1)
        unit_amount = li.get('price', {}).get('unit_amount', 0) or li.get('amount_subtotal', 0)
        unit_price = Decimal(unit_amount) / 100 if unit_amount else Decimal('0.00')
        OrderLineItem.objects.create(
            order=order,
            product_type='guide',  # unknown: you can attempt to map name->product_type
            product_id=0,
            product_name=name[:255],
            quantity=quantity,
            unit_price=unit_price,
            line_total=(unit_price * quantity),
        )

    # If the order was for a logged-in user, remove SavedBagItem rows
    if user:
        from bag.models import SavedBagItem
        SavedBagItem.objects.filter(user=user).delete()