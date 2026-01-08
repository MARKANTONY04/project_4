from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ServiceForm
from services.models import Service

@staff_member_required
def service_list(request):
    services = Service.objects.all()
    return render(request, "adminpanel/service_list.html", {"services": services})

@staff_member_required
def service_create(request):
    form = ServiceForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect("admin_service_list")
    return render(request, "adminpanel/service_form.html", {"form": form, "title": "Add Service"})

@staff_member_required
def service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    form = ServiceForm(request.POST or None, instance=service)
    if form.is_valid():
        form.save()
        return redirect("admin_service_list")
    return render(request, "adminpanel/service_form.html", {"form": form, "title": "Edit Service"})

@staff_member_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == "POST":
        service.delete()
        return redirect("admin_service_list")
    return render(request, "adminpanel/service_confirm_delete.html", {"service": service})
