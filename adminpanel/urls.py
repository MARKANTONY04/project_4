from django.urls import path
from . import views

urlpatterns = [
    path("", views.admin_dashboard, name="admin_dashboard"),

    path("subscription/add/", views.add_subscription, name="add_subscription"),
    path("subscription/edit/<int:pk>/", views.edit_subscription, name="edit_subscription"),
    path("subscription/delete/<int:pk>/", views.delete_subscription, name="delete_subscription"),

    path("class/add/", views.add_class, name="add_class"),
    path("class/edit/<int:pk>/", views.edit_class, name="edit_class"),
    path("class/delete/<int:pk>/", views.delete_class, name="delete_class"),

    path("guide/add/", views.add_guide, name="add_guide"),
    path("guide/edit/<int:pk>/", views.edit_guide, name="edit_guide"),
    path("guide/delete/<int:pk>/", views.delete_guide, name="delete_guide"),
]
