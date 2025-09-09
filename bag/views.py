#add or remove items from bag, also handles persistence

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from services.models import GymSubscription, FitnessClass, NutritionGuide


def _get_product_model(product_type):
    """Helper to return the correct model class based on product_type."""
    if product_type == "subscription":
        return GymSubscription
    elif product_type == "class":
        return FitnessClass
    elif product_type == "guide":
        return NutritionGuide
    else:
        raise ValueError("Invalid product type")


def view_bag(request):
    """A view to show the bag contents"""
    return render(request, "bag/bag.html")


def add_to_bag(request, product_type, product_id):
    """Add a product to the shopping bag"""
    model = _get_product_model(product_type)
    product = get_object_or_404(model, pk=product_id)

    quantity = int(request.POST.get("quantity", 1))
    redirect_url = request.POST.get("redirect_url", reverse("services:services_list"))

    bag = request.session.get("bag", {})

    key = f"{product_type}_{product_id}"

    if key in bag:
        bag[key]["quantity"] += quantity
    else:
        bag[key] = {
            "product_type": product_type,
            "id": product.id,
            "name": product.name if product_type != "guide" else product.title,
            "price": float(product.price),
            "quantity": quantity,
        }

    request.session["bag"] = bag
    messages.success(request, f"Added {product} to your bag")
    return redirect(redirect_url)


def update_bag(request, product_type, product_id):
    """Update the quantity of a product in the shopping bag"""
    quantity = int(request.POST.get("quantity", 0))
    key = f"{product_type}_{product_id}"
    bag = request.session.get("bag", {})

    if key in bag:
        if quantity > 0:
            bag[key]["quantity"] = quantity
            messages.success(request, f"Updated {bag[key]['name']} quantity to {quantity}")
        else:
            bag.pop(key)
            messages.success(request, "Item removed from your bag")

    request.session["bag"] = bag
    return redirect("bag:view_bag")


def remove_from_bag(request, product_type, product_id):
    """Remove the item from the shopping bag"""
    key = f"{product_type}_{product_id}"
    bag = request.session.get("bag", {})

    if key in bag:
        product_name = bag[key]["name"]
        bag.pop(key)
        messages.success(request, f"Removed {product_name} from your bag")

    request.session["bag"] = bag
    return redirect("bag:view_bag")
