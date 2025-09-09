from django.db import models
from django.conf import settings
from services.models import GymSubscription, FitnessClass, NutritionGuide

# bag model

class SavedBagItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_bag")
    content_type = models.CharField(max_length=20, choices=[
        ('subscription', 'Subscription'),
        ('class', 'Class'),
        ('guide', 'Nutrition Guide'),
    ])
    object_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s item ({self.content_type} #{self.object_id})"
