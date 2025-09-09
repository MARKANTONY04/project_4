# created with Chat GPT
# add signal to merge bag on login

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import SavedBagItem

@receiver(user_logged_in)
def merge_bag_on_login(sender, request, user, **kwargs):
    session_bag = request.session.get("bag", {})

    for key, item in session_bag.items():
        content_type = item["content_type"]
        object_id = item["object_id"]
        quantity = item["quantity"]

        bag_item, created = SavedBagItem.objects.get_or_create(
            user=user,
            content_type=content_type,
            object_id=object_id,
            defaults={"quantity": quantity},
        )
        if not created:
            bag_item.quantity += quantity
            bag_item.save()

    # Clear session bag after merge
    if "bag" in request.session:
        del request.session["bag"]
