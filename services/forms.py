from django import forms
from .models import GymSubscription, Class, NutritionGuide

class GymSubscriptionForm(forms.ModelForm):
    class Meta:
        model = GymSubscription
        fields = ['name', 'description', 'price', 'duration']

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'description', 'price', 'schedule', 'instructor']

class NutritionGuideForm(forms.ModelForm):
    class Meta:
        model = NutritionGuide
        fields = ['title', 'description', 'price', 'duration']
