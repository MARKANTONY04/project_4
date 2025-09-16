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
from django.shortcuts import render, redirect, get_object_or_404
from bag.contexts import bag_contents
from .forms import OrderForm


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
    session_id = request.GET.get("session_id")
    order = None

    if session_id:
        order = get_object_or_404(Order, stripe_session_id=session_id)

    return render(request, "checkout/success.html", {"order": order})


def cancel(request):
    return render(request, 'checkout/cancel.html')

# stripe info/functions

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    bag = request.session.get('bag', {})
    if not bag:
        return redirect('services')  # Or wherever your shop is

    current_bag = bag_contents(request)
    total = current_bag['grand_total']
    stripe_total = round(total * 100)  # cents

    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    order_form = OrderForm()

    context = {
        'order_form': order_form,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'client_secret': intent.client_secret,
        'order_form': order_form,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'client_secret': intent.client_secret,
        'grand_total': total,
        'stripe_currency': settings.STRIPE_CURRENCY,
    }
    return render(request, 'checkout/checkout.html', context)


def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    # Clear the bag
    if 'bag' in request.session:
        del request.session['bag']

    context = {
        'order': order,
    }
    return render(request, 'checkout/checkout_success.html', context)

