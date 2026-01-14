# bag/context_processors.py
from .models import SavedBagItem


def bag_contents(request):
    total_qty = 0

    if request.user.is_authenticated:
        saved = SavedBagItem.objects.filter(user=request.user)
        total_qty = sum(i.quantity for i in saved)
    else:
        session_bag = request.session.get("bag", {})
        for key, val in (session_bag or {}).items():
            # support legacy int value or dict shapes
            if isinstance(val, int):
                total_qty += int(val)
            elif isinstance(val, dict):
                q = val.get("quantity", 0)
                if isinstance(q, int) and q > 0:
                    total_qty += q

    return {"bag_total_quantity": total_qty}
