from django.urls import path
from . import views

urlpatterns = [
    path('edit/', views.update_profile, name='edit_profile'),
    path('profile-updated/', views.update_profile, name='profile_updated'),  
]
