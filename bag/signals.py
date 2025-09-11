# created with Chat GPT
# add signal to merge bag on login

# bag/signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from bag.models import SavedBagItem


def merge_session_bag_after_login(request, user):
    """
    Merge session bag into SavedBagItem after login.
    """
    session_bag = request.session.get('bag', {})

    for key, item_data in session_bag.items():
        try:
            item_type, item_id = key.rsplit('_', 1)
        except ValueError:
            continue

        quantity = item_data.get('quantity', 1)

        saved_item, created = SavedBagItem.objects.get_or_create(
            user=user,
            item_type=item_type,
            item_id=item_id,
            defaults={'quantity': quantity},
        )
        if not created:
            saved_item.quantity += quantity
            saved_item.save()

    # Clear session bag
    request.session['bag'] = {}
    request.session.modified = True


@receiver(user_logged_in)
def merge_bag_on_login(sender, request, user, **kwargs):
    merge_session_bag_after_login(request, user)
