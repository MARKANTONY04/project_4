from django.db import models
from django.contrib.auth.models import User

class GymSubscription(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in months")

    def __str__(self):
        return self.name

class Class(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    schedule = models.CharField(max_length=200)
    instructor = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class NutritionGuide(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in hours")

    def __str__(self):
        return self.title
