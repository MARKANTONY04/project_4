from django.db import models
from django.contrib.auth.models import User


class SavedBagItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_type = models.CharField(
        max_length=20,
        blank=True,
        null=True)  # newly added
    item_id = models.PositiveIntegerField(
        blank=True, null=True)         # newly added
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{
            self.user} | {
            self.item_type}:{
            self.item_id} ({
                self.quantity})"
