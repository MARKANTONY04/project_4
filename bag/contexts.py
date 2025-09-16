# bag/contexts.py
from decimal import Decimal
from django.conf import settings

from services.models import GymSubscription, FitnessClass, NutritionGuide
from .models import SavedBagItem


def bag_contents(request):
    bag_items = []
    total = Decimal("0.00")

    if request.user.is_authenticated:
        saved_items = SavedBagItem.objects.filter(user=request.user)
        for item in saved_items:
            model = None
            if item.item_type == "subscription":
                model = GymSubscription
            elif item.item_type == "class":
                model = FitnessClass
            elif item.item_type == "guide":
                model = NutritionGuide

            if model:
                try:
                    product = model.objects.get(pk=item.item_id)
                    item_total = product.price * item.quantity
                    total += item_total
                    bag_items.append({
                        "item": product,
                        "quantity": item.quantity,
                        "item_type": item.item_type,
                        "total": item_total,
                    })
                except model.DoesNotExist:
                    pass

    return {
        "bag_items": bag_items,
        "bag_total": total,
    }
