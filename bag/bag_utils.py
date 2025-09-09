from .models import SavedBagItem

# Handles anonymous vs logged-in storage seamlessly

def get_bag_items(request):
    bag_items = []

    if request.user.is_authenticated:
        # Load from database
        bag_items = list(SavedBagItem.objects.filter(user=request.user))
    else:
        # Load from session
        bag = request.session.get('bag', {})
        for key, item in bag.items():
            bag_items.append({
                'content_type': item['content_type'],
                'object_id': item['object_id'],
                'quantity': item['quantity'],
            })
    return bag_items
