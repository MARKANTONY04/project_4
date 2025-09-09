from django.shortcuts import render

# Add/remove items, handle persistence.

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from services.models import GymSubscription, FitnessClass, NutritionGuide
from .models import SavedBagItem

def add_to_bag(request, content_type, object_id):
    if request.user.is_authenticated:
        SavedBagItem.objects.update_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            defaults={'quantity': 1},
        )
    else:
        bag = request.session.get('bag', {})
        key = f"{content_type}_{object_id}"
        if key not in bag:
            bag[key] = {'content_type': content_type, 'object_id': object_id, 'quantity': 1}
        else:
            bag[key]['quantity'] += 1
        request.session['bag'] = bag

    return redirect("bag:view_bag")


def remove_from_bag(request, content_type, object_id):
    if request.user.is_authenticated:
        SavedBagItem.objects.filter(user=request.user, content_type=content_type, object_id=object_id).delete()
    else:
        bag = request.session.get('bag', {})
        key = f"{content_type}_{object_id}"
        if key in bag:
            del bag[key]
            request.session['bag'] = bag

    return redirect("bag:view_bag")


def view_bag(request):
    from .bag_utils import get_bag_items
    items = get_bag_items(request)
    return render(request, "bag/bag.html", {"bag_items": items})
