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