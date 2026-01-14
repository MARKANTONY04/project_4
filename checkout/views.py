# checkout/views.py
# checkout/views.py
import json
from decimal import Decimal

import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.http import require_POST

from bag.models import SavedBagItem
from bag.views import _get_product, _normalize_session_bag
from .forms import OrderForm
from .models import Order, OrderLineItem

stripe.api_key = settings.STRIPE_SECRET_KEY


def _get_bag_items_for_checkout(request):
    """
    Return a list of dicts:
    {product, item_type, id, quantity, unit_price, display_name}
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
                "product": product,
                "type": s.item_type,
                "id": s.item_id,
                "quantity": s.quantity,
                "unit_price": Decimal(getattr(product, "price", 0)),
                "display_name": getattr(
                    product, "name", getattr(product, "title", str(product))
                ),
            })
    else:
        session_bag = _normalize_session_bag(request.session.get("bag", {}))

        for val in session_bag.values():
            product = _get_product(val["type"], val["id"])
            if not product:
                continue

            items.append({
                "product": product,
                "type": val["type"],
                "id": val["id"],
                "quantity": val["quantity"],
                "unit_price": Decimal(getattr(product, "price", 0)),
                "display_name": getattr(
                    product, "name", getattr(product, "title", str(product))
                ),
            })

    return items


@require_POST
def create_checkout_session(request):
    """Create a Stripe Checkout Session and corresponding Order in DB."""
    bag_items = _get_bag_items_for_checkout(request)

    if not bag_items:
        return JsonResponse({"error": "Your bag is empty."}, status=400)

    line_items = []

    for item in bag_items:
        unit_amount = int((item["unit_price"] * 100).quantize(Decimal("1")))

        line_items.append({
            "price_data": {
                "currency": settings.STRIPE_CURRENCY,
                "product_data": {"name": item["display_name"]},
                "unit_amount": unit_amount,
            },
            "quantity": item["quantity"],
        })

    domain = request.build_absolute_uri("/")[:-1]

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=domain + reverse("checkout:success")
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain + reverse("checkout:cancel"),
            metadata={
                "user_id": request.user.id if request.user.is_authenticated else ""
            },
        )
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        stripe_session_id=session.id,
        full_name=request.POST.get("full_name", "Guest"),
        email=request.POST.get(
            "email",
            request.user.email if request.user.is_authenticated else "",
        ),
        phone_number=request.POST.get("phone_number", ""),
        address_line1=request.POST.get("address_line1", ""),
        address_line2=request.POST.get("address_line2", ""),
        city=request.POST.get("city", ""),
        postcode=request.POST.get("postcode", ""),
        country=request.POST.get("country", ""),
    )

    for item in bag_items:
        OrderLineItem.objects.create(
            order=order,
            product_type=item["type"],
            product_id=item["id"],
            product_name=item["display_name"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            line_total=item["unit_price"] * item["quantity"],
        )

    return JsonResponse({"id": session.id, "url": session.url})


def success(request):
    session_id = request.GET.get("session_id")
    order = None

    if session_id:
        order = get_object_or_404(Order, stripe_session_id=session_id)

    line_items = order.lineitems.all()
    total_paid = sum(item.line_total for item in line_items)

    if "bag" in request.session:
        del request.session["bag"]

    if request.user.is_authenticated:
        SavedBagItem.objects.filter(user=request.user).delete()

    return render(
        request,
        "checkout/success.html",
        {"order": order, "total_paid": total_paid},
    )


def cancel(request):
    return render(request, "checkout/cancel.html")
