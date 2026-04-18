from django.urls import path
from . import views

urlpatterns = [
    path('webhooks/payment/', views.payment_webhook, name='payment_webhook'),
    path('api/content/', views.content_list, name='content_list'),
    path('api/payment/', views.create_payment, name='create_payment'),
]
