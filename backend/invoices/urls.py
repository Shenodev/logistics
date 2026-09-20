from django.urls import path

from .views import create_refund

urlpatterns = [
    path('', create_refund, name='invoice-refund'),
]
