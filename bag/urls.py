from django.urls import path
from . import views

app_name = "bag"

urlpatterns = [
    path("", views.view_bag, name="view_bag"),
    path("add/<str:content_type>/<int:object_id>/", views.add_to_bag, name="add_to_bag"),
    path("remove/<str:content_type>/<int:object_id>/", views.remove_from_bag, name="remove_from_bag"),
]
