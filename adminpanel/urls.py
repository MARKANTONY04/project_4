from django.urls import path
from . import views

urlpatterns = [
    path("services/", views.service_list, name="admin_service_list"),
    path("services/add/", views.service_create, name="admin_service_add"),
    path("services/<int:pk>/edit/", views.service_edit, name="admin_service_edit"),
    path("services/<int:pk>/delete/", views.service_delete, name="admin_service_delete"),
]
