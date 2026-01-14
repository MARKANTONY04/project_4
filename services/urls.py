from django.urls import path
from . import views

urlpatterns = [path('', views.services_list, name='services_list'), path(
    '<str:service_type>/<int:pk>/', views.service_detail, name='service_detail'), ]
