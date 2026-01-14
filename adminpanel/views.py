from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from services.models import FitnessClass, GymSubscription, NutritionGuide
from .forms import FitnessClassForm, GymSubscriptionForm, NutritionGuideForm


def staff_check(user):
    if user.is_staff:
        return True
    raise PermissionDenied


staff_only = user_passes_test(staff_check)


@staff_only
def admin_dashboard(request):
    context = {
        "subscriptions": GymSubscription.objects.all(),
        "classes": FitnessClass.objects.all(),
        "guides": NutritionGuide.objects.all(),
    }
    return render(request, "adminpanel/dashboard.html", context)


@staff_only
def subscription_list(request):
    subscriptions = GymSubscription.objects.all()
    return render(
        request,
        "adminpanel/service_list.html",
        {"subscriptions": subscriptions},
    )


@staff_only
def class_list(request):
    classes = FitnessClass.objects.all()
    return render(request, "adminpanel/class_list.html", {"classes": classes})


@staff_only
def guide_list(request):
    guides = NutritionGuide.objects.all()
    return render(request, "adminpanel/guide_list.html", {"guides": guides})


# ---------- Subscriptions ----------


@staff_only
def add_subscription(request):
    form = GymSubscriptionForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("admin_dashboard")
    return render(
        request,
        "adminpanel/add.html",
        {"form": form, "title": "Add Subscription"},
    )


@staff_only
def edit_subscription(request, pk):
    obj = get_object_or_404(GymSubscription, pk=pk)
    form = GymSubscriptionForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("admin_dashboard")
    return render(
        request,
        "adminpanel/edit.html",
        {"form": form, "title": "Edit Subscription"},
    )


@staff_only
def delete_subscription(request, pk):
    obj = get_object_or_404(GymSubscription, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("admin_dashboard")
    return render(request, "adminpanel/delete.html", {"obj": obj})


# ---------- Classes ----------


@staff_only
def add_class(request):
    form = FitnessClassForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("admin_dashboard")
    return render(
        request,
        "adminpanel/add.html",
        {"form": form, "title": "Add Fitness Class"},
    )


@staff_only
def edit_class(request, pk):
    obj = get_object_or_404(FitnessClass, pk=pk)
    form = FitnessClassForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("admin_dashboard")
    return render(
        request,
        "adminpanel/edit.html",
        {"form": form, "title": "Edit Fitness Class"},
    )


@staff_only
def delete_class(request, pk):
    obj = get_object_or_404(FitnessClass, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("admin_dashboard")
    return render(request, "adminpanel/delete.html", {"obj": obj})


# ---------- Guides ----------


@staff_only
def add_guide(request):
    form = NutritionGuideForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("admin_dashboard")
    return render(
        request,
        "adminpanel/add.html",
        {"form": form, "title": "Add Nutrition Guide"},
    )


@staff_only
def edit_guide(request, pk):
    obj = get_object_or_404(NutritionGuide, pk=pk)
    form = NutritionGuideForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("admin_dashboard")
    return render(
        request,
        "adminpanel/edit.html",
        {"form": form, "title": "Edit Nutrition Guide"},
    )


@staff_only
def delete_guide(request, pk):
    obj = get_object_or_404(NutritionGuide, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("admin_dashboard")
    return render(request, "adminpanel/delete.html", {"obj": obj})
