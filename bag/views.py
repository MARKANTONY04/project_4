#add or remove items from bag, also handles persistence

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from services.models import GymSubscription, FitnessClass, NutritionGuide
from .models import SavedBagItem

def _get_product(item_type, item_id):
    """Helper to fetch the right product model based on type"""
    if item_type == "subscription":
        return get_object_or_404(GymSubscription, pk=item_id)
    elif item_type == "class":
        return get_object_or_404(FitnessClass, pk=item_id)
    elif item_type == "guide":
        return get_object_or_404(NutritionGuide, pk=item_id)
    return None


def view_bag(request):
    """Show the bag page"""
    return render(request, "bag/bag.html")


def add_to_bag(request, item_type, item_id):
    """Add an item to the bag (session or database depending on user)"""
    product = _get_product(item_type, item_id)
    quantity = int(request.POST.get("quantity", 1))
    redirect_url = request.POST.get("redirect_url", reverse("bag:view_bag"))

    if request.user.is_authenticated:
        # Save in DB
        bag_item, created = SavedBagItem.objects.get_or_create(
            user=request.user, item_type=item_type, item_id=item_id,
            defaults={"quantity": quantity}
        )
        if not created:
            bag_item.quantity += quantity
            bag_item.save()
    else:
        # Save in session
        bag = request.session.get("bag", {})
        key = f"{item_type}_{item_id}"
        if key in bag:
            bag[key]["quantity"] += quantity
        else:
            bag[key] = {"type": item_type, "id": item_id, "quantity": quantity}
        request.session["bag"] = bag

    messages.success(request, f"Added {quantity} × {product} to your bag")
    return redirect(redirect_url)


def update_bag(request, item_type, item_id):
    """Update quantity of an item in the bag"""
