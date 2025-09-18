# checkout/views.py
import json
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.mail import send_mail

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from bag.views import _normalize_session_bag, _get_product
from bag.models import SavedBagItem
from .models import Order, OrderLineItem
from .forms import OrderForm
from bag.contexts import bag_contents


def _get_bag_items_for_checkout(request):
    """
    Return a list of dicts: {product, item_type, id, quantity, unit_price, display_name}
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
        for _, val in session_bag.items():
            product = _get_product(val['type'], val['id'])
            if not product:
                continue
            items.append({
                'product': product,
                'type': val['type'],
                'id': val['id'],
                'quantity': val['quantity'],
                'unit_price': Decimal(getattr(product, 'price', 0)),
                'display_name': getattr(product, 'name', getattr(product, 'title', str(product)))
            })
    return items


@require_POST
def create_checkout_session(request):
    """
    Create a Stripe Checkout Session and corresponding Order in DB.
    """
    bag_items = _get_bag_items_for_checkout(request)
    if not bag_items:
        return JsonResponse({'error': 'Your bag is empty.'}, status=400)

    line_items = []
    for it in bag_items:
        unit_amount = int((it['unit_price'] * 100).quantize(Decimal('1')))
        line_items.append({
            'price_data': {
                'currency': settings.STRIPE_CURRENCY,
                'product_data': {'name': it['display_name']},
                'unit_amount': unit_amount,
            },
            'quantity': it['quantity'],
        })

    DOMAIN = request.build_absolute_uri('/')[:-1]

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=DOMAIN + reverse('checkout:success') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=DOMAIN + reverse('checkout:cancel'),
            metadata={'user_id': request.user.id if request.user.is_authenticated else ''},
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    # Create the Order in DB and link Stripe session
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        stripe_session_id=session.id,
        full_name=request.POST.get("full_name", "Guest"),
        email=request.POST.get("email", request.user.email if request.user.is_authenticated else ""),
        phone_number=request.POST.get("phone_number", ""),
        address_line1=request.POST.get("address_line1", ""),
        address_line2=request.POST.get("address_line2", ""),
        city=request.POST.get("city", ""),
        postcode=request.POST.get("postcode", ""),
        country=request.POST.get("country", ""),
    )

    # Add line items to the Order
    for it in bag_items:
        OrderLineItem.objects.create(
            order=order,
            product_type=it['type'],
            product_id=it['id'],
            product_name=it['display_name'],
            quantity=it['quantity'],
            unit_price=it['unit_price'],
            line_total=it['unit_price'] * it['quantity'],
        )

    return JsonResponse({'id': session.id, 'url': session.url})


def success(request):
    session_id = request.GET.get("session_id")
    order = None

    if session_id:
        order = get_object_or_404(Order, stripe_session_id=session_id)

    # Calculate total paid (sum of line totals)
    total_paid = sum(item.line_total for item in order.lineitems.all())

    return render(
        request,
        "checkout/success.html",
        {
            "order": order,
            "total_paid": total_paid,  # pass it to template
        },
    )



def cancel(request):
    return render(request, 'checkout/cancel.html')
