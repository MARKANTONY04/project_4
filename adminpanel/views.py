from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from services.models import GymSubscription, FitnessClass, NutritionGuide
from .forms import GymSubscriptionForm, FitnessClassForm, NutritionGuideForm
from django.contrib.auth.decorators import user_passes_test

def staff_check(user):
    return user.is_staff


@user_passes_test(staff_check)
def subscription_list(request):
    subscriptions = GymSubscription.objects.all()
    return render(request, "adminpanel/service_list.html", {"subscriptions": subscriptions})


@user_passes_test(staff_check)
def class_list(request):
    classes = FitnessClass.objects.all()
    return render(request, "adminpanel/class_list.html", {"classes": classes})


@user_passes_test(staff_check)
def guide_list(request):
    guides = NutritionGuide.objects.all()
    return render(request, "adminpanel/guide_list.html", {"guides": guides})

@staff_member_required
def admin_dashboard(request):
    return render(request, "adminpanel/dashboard.html", {
        "subscriptions": GymSubscription.objects.all(),
        "classes": FitnessClass.objects.all(),
        "guides": NutritionGuide.objects.all(),
    })


# ---------- Subscriptions ----------

@staff_member_required
def add_subscription(request):
    form = GymSubscriptionForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("admin_dashboard")
    return render(request, "adminpanel/add.html", {"form": form, "title": "Add Subscription"})


@staff_member_required
def edit_subscription(request, pk):
    obj = get_object_or_404(GymSubscription, pk=pk)
    form = GymSubscriptionForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("admin_dashboard")
    return render(request, "adminpanel/edit.html", {"form": form, "title": "Edit Subscription"})


@staff_member_required
def delete_subscription(request, pk):
    obj = get_object_or_404(GymSubscription, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("admin_dashboard")
    return render(request, "adminpanel/delete.html", {"obj": obj})


# ---------- Classes ----------

@staff_member_required
def add_class(request):
    form = FitnessClassForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("admin_dashboard")
    return render(request, "adminpanel/add.html", {"form": form, "title": "Add Fitness Class"})


@staff_member_required
def edit_class(request, pk):
    obj = get_object_or_404(FitnessClass, pk=pk)
    form = FitnessClassForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("admin_dashboard")
    return render(request, "adminpanel/edit.html", {"form": form, "title": "Edit Fitness Class"})


@staff_member_required
def delete_class(request, pk):
    obj = get_object_or_404(FitnessClass, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("admin_dashboard")
    return render(request, "adminpanel/delete.html", {"obj": obj})


# ---------- Guides ----------

@staff_member_required
def add_guide(request):
    form = NutritionGuideForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("admin_dashboard")
    return render(request, "adminpanel/add.html", {"form": form, "title": "Add Nutrition Guide"})


@staff_member_required
def edit_guide(request, pk):
    obj = get_object_or_404(NutritionGuide, pk=pk)
    form = NutritionGuideForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect("admin_dashboard")
    return render(request, "adminpanel/edit.html", {"form": form, "title": "Edit Nutrition Guide"})


@staff_member_required
def delete_guide(request, pk):
    obj = get_object_or_404(NutritionGuide, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("admin_dashboard")
    return render(request, "adminpanel/delete.html", {"obj": obj})
