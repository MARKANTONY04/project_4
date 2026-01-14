from django.db import models


class GymSubscription(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration_months = models.PositiveIntegerField(
        default=1)  # default = 1 month
    description = models.TextField(
        default="No description provided.")  # safe default

    def __str__(self):
        return self.name


class FitnessClass(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00)  # default price
    schedule = models.CharField(max_length=200,
                                default="To be announced")  # default schedule
    description = models.TextField(default="No description provided.")

    def __str__(self):
        return self.name


class NutritionGuide(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    content_summary = models.TextField(
        default="Content coming soon.")  # renamed from description

    def __str__(self):
        return self.title
