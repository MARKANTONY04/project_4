# add to handle merging session bag after login and upading bag

# used chat gpt to reformat to fix errors

# bag/views.py
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from services.models import GymSubscription, FitnessClass, NutritionGuide
from .models import SavedBagItem


# --------- helpers ---------
MODEL_MAP = {
    "subscription": GymSubscription,
    "class": FitnessClass,
    "guide": NutritionGuide,
}

def _get_product(item_type, pk):
    Model = MODEL_MAP.get(item_type)
    if not Model:
        return None
    return get_object_or_404(Model, pk=pk)


def _normalize_session_bag(session_bag):
    """
    Make sure every entry in the session bag has the expected keys:
    {
        "<type>:<id>": {"type": "...", "id": <int>, "quantity": <int>, "price": "<str-decimal>"}
    }
    Any malformed entries are skipped.
    """
    normalized = {}
    for key, value in (session_bag or {}).items():
        # value might be an int, a bare dict missing fields, or the correct shape
        if isinstance(value, int):
            # legacy shape like: "subscription:1": 2  -> infer from key
            if ":" not in key:
                continue
            itype, sid = key.split(":", 1)
            try:
                sid_int = int(sid)
            except ValueError:
                continue
            normalized[key] = {
                "type": itype,
                "id": sid_int,
                "quantity": value,
            }
            continue

        if not isinstance(value, dict):
            continue

        # try to infer missing fields
        itype = value.get("type")
        iid = value.get("id")
        qty = value.get("quantity", 1)

        # if missing type/id, infer from key
        if (itype is None or iid is None) and ":" in key:
            k_type, k_sid = key.split(":", 1)
            if itype is None:
                itype = k_type
            if iid is None:
                try:
                    iid = int(k_sid)
                except ValueError:
                    iid = None

        # final validation
        if itype not in MODEL_MAP or not isinstance(qty, int) or qty < 1 or iid is None:
            continue

        normalized[f"{itype}:{iid}"] = {
            "type": itype,
            "id": int(iid),
            "quantity": int(qty),
        }

    return normalized


def _session_add(request, item_type, item_id, quantity):
    bag = request.session.get("bag", {})
    key = f"{item_type}:{item_id}"

    # normalize first, then mutate
    bag = _normalize_session_bag(bag)

    existing = bag.get(key)
    if existing:
        existing["quantity"] += quantity
    else:
        bag[key] = {"type": item_type, "id": item_id, "quantity": quantity}

    request.session["bag"] = bag
    request.session.modified = True


def _session_update(request, item_type, item_id, quantity):
    bag = request.session.get("bag", {})
    bag = _normalize_session_bag(bag)
    key = f"{item_type}:{item_id}"

    if quantity < 1:
        bag.pop(key, None)
    else:
        if key in bag:
            bag[key]["quantity"] = quantity
        else:
            bag[key] = {"type": item_type, "id": item_id, "quantity": quantity}

    request.session["bag"] = bag
    request.session.modified = True


def _session_remove(request, item_type, item_id):
    bag = request.session.get("bag", {})
    bag = _normalize_session_bag(bag)
    key = f"{item_type}:{item_id}"
    bag.pop(key, None)
    request.session["bag"] = bag
    request.session.modified = True


def _build_line(product, item_type, quantity):
    """Return a dict the template expects."""
    # price attr names differ slightly
    if item_type == "subscription":
        unit_price = Decimal(getattr(product, "price"))
        display_name = getattr(product, "name")
        desc = getattr(product, "description", "")
    elif item_type == "class":
        unit_price = Decimal(getattr(product, "price"))
        display_name = getattr(product, "name")
        desc = getattr(product, "description", "")
    else:  # guide
        unit_price = Decimal(getattr(product, "price"))
        display_name = getattr(product, "title")
        desc = getattr(product, "content_summary", "")

    subtotal = unit_price * quantity
    return {
        "product": product,
        "type": item_type,
        "id": product.id,
        "price": unit_price,
        "quantity": quantity,
        "subtotal": subtotal,
        "display_name": display_name,
        "description": desc,
    }


# --------- views ---------
def view_bag(request):
    """
    Build a unified list of bag lines from either:
      - session (guest)
      - SavedBagItem (authenticated)
    """
    bag_items = []
    grand_total = Decimal("0.00")

    if request.user.is_authenticated:
        saved = SavedBagItem.objects.filter(user=request.user)

        for s in saved:
            product = None
            if s.item_type == "subscription":
                product = GymSubscription.objects.filter(pk=s.item_id).first()
            elif s.item_type == "class":
                product = FitnessClass.objects.filter(pk=s.item_id).first()
            elif s.item_type == "guide":
                product = NutritionGuide.objects.filter(pk=s.item_id).first()

            if not product:
                # clean up invalid rows silently
                s.delete()
                continue

            line = _build_line(product, s.item_type, s.quantity)
            bag_items.append(line)
            grand_total += line["subtotal"]
    else:
        session_bag = _normalize_session_bag(request.session.get("bag", {}))
        for key, val in session_bag.items():
            item_type = val["type"]
            item_id = val["id"]
            quantity = val["quantity"]
            product = _get_product(item_type, item_id)
            line = _build_line(product, item_type, quantity)
            bag_items.append(line)
            grand_total += line["subtotal"]

    context = {
        "bag_items": bag_items,
        "grand_total": grand_total,
    }
    return render(request, "bag/bag.html", context)


@require_POST
def add_to_bag(request, item_type, item_id):
    if item_type not in MODEL_MAP:
        messages.error(request, "Unknown item type.")
        messages.success(request, "Added to bag.")
        return redirect("bag:view_bag")


    quantity = int(request.POST.get("quantity", 1))
    if quantity < 1:
        quantity = 1

    # Make sure product exists (404 if not)
    _get_product(item_type, item_id)

    if request.user.is_authenticated:
        obj, created = SavedBagItem.objects.get_or_create(
            user=request.user, item_type=item_type, item_id=item_id,
            defaults={"quantity": quantity}
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
        messages.success(request, "Bag updated.")
        return redirect("bag:view_bag")



    quantity = int(request.POST.get("quantity", 1))
    if quantity < 0:
        quantity = 0

    _get_product(item_type, item_id)

    if request.user.is_authenticated:
        try:
            obj = SavedBagItem.objects.get(
                user=request.user, item_type=item_type, item_id=item_id
            )
            if quantity < 1:
                obj.delete()
            else:
                obj.quantity = quantity
                obj.save()
        except SavedBagItem.DoesNotExist:
            if quantity > 0:
                SavedBagItem.objects.create(
                    user=request.user, item_type=item_type, item_id=item_id, quantity=quantity
                )
    else:
        _session_update(request, item_type, item_id, quantity)

    messages.success(request, "Bag updated.")
    return redirect("bag:view_bag")



@require_POST
def remove_from_bag(request, item_type, item_id):
    if item_type not in MODEL_MAP:
        messages.error(request, "Unknown item type.")
        messages.success(request, "Item removed.")
        return redirect("bag:view_bag")



    _get_product(item_type, item_id)

    if request.user.is_authenticated:
        SavedBagItem.objects.filter(
            user=request.user, item_type=item_type, item_id=item_id
        ).delete()
    else:
        _session_remove(request, item_type, item_id)

    messages.success(request, "Item removed.")
    return redirect("bag:view_bag")


def merge_session_bag_after_login(request):
    """
    Dummy endpoint just to handle redirect after login.
    The real merging is done in signals.py.
    """
    messages.success(request, "Your bag has been updated after login.")
    return redirect("bag:view_bag") 