# checkout/urls.py
from django.urls import path
from . import views
from . import webhook

app_name = 'checkout'

urlpatterns = [
    path('create-session/', views.create_checkout_session, name='create_session'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]
