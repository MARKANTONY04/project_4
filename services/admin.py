from django.contrib import admin
from .models import GymSubscription, FitnessClass, NutritionGuide  # ✅ use FitnessClass


@admin.register(GymSubscription)
class GymSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "duration_months")


@admin.register(FitnessClass)  
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "schedule")


@admin.register(NutritionGuide)
class NutritionGuideAdmin(admin.ModelAdmin):
    list_display = ("title", "price")
