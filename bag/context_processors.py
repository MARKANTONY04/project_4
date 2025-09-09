from .bag_utils import get_bag_items

# bag context processor

def bag_contents(request):
    return {
        'bag_items': get_bag_items(request),
    }
