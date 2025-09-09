#add or remove items from bag, also handles persistence

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from services.models import Subscription, GymClass, NutritionGuide
from .models import SavedBagItem

def add_to_bag(request, item_type, item_id):
    """Add a product to the bag"""
    quantity = int(request.POST.get("quantity", 1))
    redirect_url = request.POST.get("redirect_url", "/")

    # Determine product
    if item_type == "subscription":
        product = get_object_or_404(Subscription, id=item_id)
        price = product.price
    elif item_type == "class":
        product = get_object_or_404(GymClass, id=item_id)
        price = product.price
    elif item_type == "guide":
        product = get_object_or_404(NutritionGuide, id=item_id)
        price = product.price
    else:
        messages.error(request, "Invalid product type.")
        return redirect(redirect_url)

    if request.user.is_authenticated:
        # Logged-in: save to DB
        saved_item, created = SavedBagItem.objects.get_or_create(
            user=request.user,
            item_type=item_type,
            item_id=item_id,
            defaults={"quantity": quantity}
        )
        if not created:
            saved_item.quantity += quantity
            saved_item.save()
        messages.success(request, f"Added {quantity} x {product.name if item_type != 'guide' else product.title} to your bag.")
    else:
        # Guest: save in session
        session_bag = request.session.get("bag", {})
        key = f"{item_type}-{item_id}"
        if key in session_bag:
            session_bag[key]["quantity"] += quantity
        else:
            session_bag[key] = {
                "id": item_id,
                "type": item_type,
                "quantity": quantity,
            }
        request.session["bag"] = session_bag
        messages.success(request, f"Added {quantity} x {product.name if item_type != 'guide' else product.title} to your bag.")

    return redirect(redirect_url)


def update_bag(request, item_type, item_id):
    """Update quantity of an item in the bag"""
    quantity = int(request.POST.get("quantity", 1))
    redirect_url = request.POST.get("redirect_url", "/")

    if request.user.is_authenticated:
        try:
            saved_item = SavedBagItem.objects.get(user=request.user, item_type=item_type, item_id=item_id)
            if quantity > 0:
                saved_item.quantity = quantity
                saved_item.save()
                messages.success(request, "Bag updated successfully.")
            else:
                saved_item.delete()
                messages.success(request, "Item removed from your bag.")
        except SavedBagItem.DoesNotExist:
            messages.error(request, "Item not found in your bag.")
    else:
        session_bag = request.session.get("bag", {})
        key = f"{item_type}-{item_id}"
        if key in session_bag:
            if quantity > 0:
                session_bag[key]["quantity"] = quantity
            else:
                del session_bag[key]
            request.session["bag"] = session_bag
            messages.success(request, "Bag updated successfully.")
        else:
            messages.error(request, "Item not found in your bag.")

    return redirect(redirect_url)


def remove_from_bag(request, item_type, item_id):
    """Remove an item from the bag"""
    redirect_url = request.POST.get("redirect_url", "/")

    if request.user.is_authenticated:
        try:
            item = SavedBagItem.objects.get(user=request.user, item_type=item_type, item_id=item_id)
            item.delete()
            messages.success(request, "Item removed from your bag.")
        except SavedBagItem.DoesNotExist:
            messages.error(request, "Item not found in your bag.")
    else:
        session_bag = request.session.get("bag", {})
        key = f"{item_type}-{item_id}"
        if key in session_bag:
            del session_bag[key]
            request.session["bag"] = session_bag
            messages.success(request, "Item removed from your bag.")
        else:
            messages.error(request, "Item not found in your bag.")

    return redirect(redirect_url)
