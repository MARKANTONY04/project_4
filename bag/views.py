# add to handle merging session bag after login and updating bag

# used chat gpt to help reformat this file to fix errors by cleaning up code

# bag/views.py
from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from services.models import FitnessClass, GymSubscription, NutritionGuide
from .models import SavedBagItem


MODEL_MAP = {
    "subscription": GymSubscription,
    "class": FitnessClass,
    "guide": NutritionGuide,
}


def _get_product(item_type, pk):
    model = MODEL_MAP.get(item_type)
    if not model:
        return None
    return get_object_or_404(model, pk=pk)


def _normalize_session_bag(session_bag):
    """
    Ensure all entries in the session bag have a consistent structure:
    {
        "<type>:<id>": {"type": "...", "id": int, "quantity": int}
    }
    """
    normalized = {}

    for key, value in (session_bag or {}).items():
        if isinstance(value, int):
            if ":" not in key:
                continue

            item_type, sid = key.split(":", 1)
            try:
                sid_int = int(sid)
            except ValueError:
                continue

            normalized[key] = {
                "type": item_type,
                "id": sid_int,
                "quantity": value,
            }
            continue

        if not isinstance(value, dict):
            continue

        item_type = value.get("type")
        item_id = value.get("id")
        quantity = value.get("quantity", 1)

        if (item_type is None or item_id is None) and ":" in key:
            key_type, key_id = key.split(":", 1)
            if item_type is None:
                item_type = key_type
            if item_id is None:
                try:
                    item_id = int(key_id)
                except ValueError:
                    item_id = None

        if (
            item_type not in MODEL_MAP
            or not isinstance(quantity, int)
            or quantity < 1
            or item_id is None
        ):
            continue

        normalized[f"{item_type}:{item_id}"] = {
            "type": item_type,
            "id": int(item_id),
            "quantity": int(quantity),
        }

    return normalized


def _session_add(request, item_type, item_id, quantity):
    bag = _normalize_session_bag(request.session.get("bag", {}))
    key = f"{item_type}:{item_id}"

    if key in bag:
        bag[key]["quantity"] += quantity
    else:
        bag[key] = {"type": item_type, "id": item_id, "quantity": quantity}

    request.session["bag"] = bag
    request.session.modified = True


def _session_update(request, item_type, item_id, quantity):
    bag = _normalize_session_bag(request.session.get("bag", {}))
    key = f"{item_type}:{item_id}"

    if quantity < 1:
        bag.pop(key, None)
    elif key in bag:
        bag[key]["quantity"] = quantity
    else:
        bag[key] = {"type": item_type, "id": item_id, "quantity": quantity}

    request.session["bag"] = bag
    request.session.modified = True


def _session_remove(request, item_type, item_id):
    bag = _normalize_session_bag(request.session.get("bag", {}))
    bag.pop(f"{item_type}:{item_id}", None)
    request.session["bag"] = bag
    request.session.modified = True


def _build_line(product, item_type, quantity):
    if item_type == "guide":
        display_name = product.title
        description = getattr(product, "content_summary", "")
    else:
        display_name = product.name
        description = getattr(product, "description", "")

    unit_price = Decimal(product.price)
    subtotal = unit_price * quantity

    return {
        "product": product,
        "type": item_type,
        "id": product.id,
        "price": unit_price,
        "quantity": quantity,
        "subtotal": subtotal,
        "display_name": display_name,
        "description": description,
    }


def view_bag(request):
    bag_items = []
    grand_total = Decimal("0.00")

    if request.user.is_authenticated:
        saved_items = SavedBagItem.objects.filter(user=request.user)

        for saved in saved_items:
            product = _get_product(saved.item_type, saved.item_id)
            if not product:
                saved.delete()
                continue

            line = _build_line(product, saved.item_type, saved.quantity)
            bag_items.append(line)
            grand_total += line["subtotal"]
    else:
        session_bag = _normalize_session_bag(request.session.get("bag", {}))

        for item in session_bag.values():
            product = _get_product(item["type"], item["id"])
            line = _build_line(product, item["type"], item["quantity"])
            bag_items.append(line)
            grand_total += line["subtotal"]

    return render(
        request,
        "bag/bag.html",
        {"bag_items": bag_items, "grand_total": grand_total},
    )


@require_POST
def add_to_bag(request, item_type, item_id):
    if item_type not in MODEL_MAP:
        messages.error(request, "Unknown item type.")
        return redirect("bag:view_bag")

    quantity = max(1, int(request.POST.get("quantity", 1)))
    _get_product(item_type, item_id)

    if request.user.is_authenticated:
        obj, created = SavedBagItem.objects.get_or_create(
            user=request.user,
            item_type=item_type,
            item_id=item_id,
            defaults={"quantity": quantity},
        )
        if not created:
            obj.quantity += quantity
            obj.save()
    else:
        _session_add(request, item_type, item_id, quantity)

    messages.success(request, "Added to bag.")
    return redirect("bag:view_bag")


@require_POST
def update_bag(request, item_type, item_id):
    if item_type not in MODEL_MAP:
        messages.error(request, "Unknown item type.")
        return redirect("bag:view_bag")

    quantity = max(0, int(request.POST.get("quantity", 0)))
    _get_product(item_type, item_id)

    if request.user.is_authenticated:
        try:
            obj = SavedBagItem.objects.get(
                user=request.user,
                item_type=item_type,
                item_id=item_id,
            )
            if quantity < 1:
                obj.delete()
            else:
                obj.quantity = quantity
                obj.save()
        except SavedBagItem.DoesNotExist:
            if quantity > 0:
                SavedBagItem.objects.create(
                    user=request.user,
                    item_type=item_type,
                    item_id=item_id,
                    quantity=quantity,
                )
    else:
        _session_update(request, item_type, item_id, quantity)

    messages.success(request, "Bag updated.")
    return redirect("bag:view_bag")


@require_POST
def remove_from_bag(request, item_type, item_id):
    if item_type not in MODEL_MAP:
        messages.error(request, "Unknown item type.")
        return redirect("bag:view_bag")

    _get_product(item_type, item_id)

    if request.user.is_authenticated:
        SavedBagItem.objects.filter(
            user=request.user,
            item_type=item_type,
            item_id=item_id,
        ).delete()
    else:
        _session_remove(request, item_type, item_id)

    messages.success(request, "Item removed.")
    return redirect("bag:view_bag")


def merge_session_bag_after_login(request):
    messages.success(request, "Your bag has been updated after login.")
    return redirect("bag:view_bag")
