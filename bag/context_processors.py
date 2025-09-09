from .models import SavedBagItem
from services.models import GymSubscription, FitnessClass, NutritionGuide

def bag_contents(request):
    bag_items = []
    bag_total_quantity = 0

    if request.user.is_authenticated:
        # Logged-in user: fetch saved items from DB
        saved_items = SavedBagItem.objects.filter(user=request.user)
        for item in saved_items:
            if item.item_type == "subscription":
                product = GymSubscription.objects.filter(pk=item.item_id).first()
            elif item.item_type == "class":
                product = FitnessClass.objects.filter(pk=item.item_id).first()
            elif item.item_type == "guide":
                product = NutritionGuide.objects.filter(pk=item.item_id).first()
            else:
                product = None

            if product:
                bag_items.append({
                    "type": item.item_type,
                    "id": item.item_id,
                    "product": product,
                    "quantity": item.quantity,
                })
                bag_total_quantity += item.quantity

    else:
        # Guest user: fetch from session
        session_bag = request.session.get("bag", {})
        for key, item in session_bag.items():
            item_type = item.get("type")
            item_id = item.get("id")
            quantity = item.get("quantity", 0)

            if item_type == "subscription":
                product = GymSubscription.objects.filter(pk=item_id).first()
            elif item_type == "class":
                product = FitnessClass.objects.filter(pk=item_id).first()
            elif item_type == "guide":
                product = NutritionGuide.objects.filter(pk=item_id).first()
            else:
                product = None

            if product:
                bag_items.append({
                    "type": item_type,
                    "id": item_id,
                    "product": product,
                    "quantity": quantity,
                })
                bag_total_quantity += quantity

    return {
        "bag_items": bag_items,
        "bag_total_quantity": bag_total_quantity,
    }

