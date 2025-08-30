from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import GymSubscription, Class, NutritionGuide
from .forms import GymSubscriptionForm, ClassForm, NutritionGuideForm

def gym_subscriptions(request):
    subscriptions = GymSubscription.objects.all()
    return render(request, 'services/gym_subscriptions.html', {'subscriptions': subscriptions})

def classes(request):
    available_classes = Class.objects.all()
    return render(request, 'services/classes.html', {'classes': available_classes})

def nutrition_guides(request):
    guides = NutritionGuide.objects.all()
    return render(request, 'services/nutrition_guides.html', {'guides': guides})

@login_required
def purchase_gym_subscription(request, subscription_id):
    subscription = GymSubscription.objects.get(id=subscription_id)
    
    return redirect('services:thank_you')

@login_required
def purchase_class(request, class_id):
    gym_class = Class.objects.get(id=class_id)
    
    return redirect('services:thank_you')

@login_required
def purchase_nutrition_guide(request, guide_id):
    nutrition_guide = NutritionGuide.objects.get(id=guide_id)
    
    return redirect('services:thank_you')

def thank_you(request):
    return render(request, 'services/thank_you.html')
