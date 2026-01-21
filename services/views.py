#chat gpt helped create this views.py file
from django.shortcuts import render, redirect, get_object_or_404
from .models import GymSubscription, FitnessClass, NutritionGuide


def services_list(request):
    subscriptions = GymSubscription.objects.all()
    classes = FitnessClass.objects.all()
    guides = NutritionGuide.objects.all()

    context = {
        'subscriptions': subscriptions,
        'classes': classes,
        'guides': guides,
    }
    return render(request, 'services/services.html', context)


def service_detail(request, service_type, pk):
    if service_type == "subscription":
        service = get_object_or_404(GymSubscription, pk=pk)
    elif service_type == "class":
        service = get_object_or_404(FitnessClass, pk=pk)
    elif service_type == "guide":
        service = get_object_or_404(NutritionGuide, pk=pk)
    else:
        return redirect("services_list")

    return render(request,
                  "services/service_detail.html",
                  {"service": service})
