from .models import SavedBagItem

def bag_contents(request):
    bag_items = []
    bag_total_quantity = 0

    if request.user.is_authenticated:
        # Logged-in user: fetch saved items
        saved_items = SavedBagItem.objects.filter(user=request.user)
        bag_items = saved_items
        bag_total_quantity = sum(item.quantity for item in saved_items)
    else:
        # Guest user: check session
        session_bag = request.session.get("bag", {})
        bag_total_quantity = sum(item["quantity"] for item in session_bag.values())

    return {
        "bag_total_quantity": bag_total_quantity,
    }
