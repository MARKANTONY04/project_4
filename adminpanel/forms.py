from django import forms
from services.models import GymSubscription, FitnessClass, NutritionGuide


class GymSubscriptionForm(forms.ModelForm):
    class Meta:
        model = GymSubscription
        fields = "__all__"


class FitnessClassForm(forms.ModelForm):
    class Meta:
        model = FitnessClass
        fields = "__all__"


class NutritionGuideForm(forms.ModelForm):
    class Meta:
        model = NutritionGuide
        fields = "__all__"
