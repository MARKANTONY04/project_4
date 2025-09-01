from django.contrib import admin
from .models import GymSubscription, Class, NutritionGuide

admin.site.register(GymSubscription)
admin.site.register(Class)
admin.site.register(NutritionGuide)
