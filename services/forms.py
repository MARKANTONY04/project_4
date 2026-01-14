from django import forms
from .models import GymSubscription, FitnessClass, NutritionGuide


class GymSubscriptionForm(forms.ModelForm):
    class Meta:
        model = GymSubscription
        fields = ['name', 'price', 'duration_months', 'description']
        widgets = {
            'description': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Enter subscription details...'}),
        }


class FitnessClassForm(forms.ModelForm):
    class Meta:
        model = FitnessClass
        fields = ['name', 'price', 'schedule', 'description']
        widgets = {
            'schedule': forms.TextInput(
                attrs={
                    'placeholder': 'E.g., Mondays at 6 PM'}),
            'description': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Enter class details...'}),
        }


class NutritionGuideForm(forms.ModelForm):
    class Meta:
        model = NutritionGuide
        fields = ['title', 'price', 'content_summary']
        widgets = {
            'content_summary': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Short summary of the guide...'}),
        }
# Note: The forms include basic widgets and placeholders for better user
# experience.
