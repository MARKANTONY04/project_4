# created with Chat GPT
# add signal to merge bag on login

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import SavedBagItem

@receiver(user_logged_in)
def merge_session_bag(sender, request, user, **kwargs):
    """Merge session bag into user's saved bag on login."""
    session_bag = request.session.get("bag", {})

    for key, item in session_bag.items():
        item_type = item.get("type")
        item_id = item.get("id")
        quantity = item.get("quantity", 1)

        saved_item, created = SavedBagItem.objects.get_or_create(
            user=user,
            item_type=item_type,
            item_id=item_id,
            defaults={"quantity": quantity},
        )
        if not created:
            saved_item.quantity += quantity
            saved_item.save()

    # Clear the session bag after merge
    request.session["bag"] = {}
