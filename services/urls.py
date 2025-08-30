from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('subscriptions/', views.gym_subscriptions, name='gym_subscriptions'),
    path('classes/', views.classes, name='classes'),
    path('nutrition-guides/', views.nutrition_guides, name='nutrition_guides'),
    path('purchase/subscription/<int:subscription_id>/', views.purchase_gym_subscription, name='purchase_gym_subscription'),
    path('purchase/class/<int:class_id>/', views.purchase_class, name='purchase_class'),
    path('purchase/guide/<int:guide_id>/', views.purchase_nutrition_guide, name='purchase_nutrition_guide'),
    path('thank-you/', views.thank_you, name='thank_you'),
]
