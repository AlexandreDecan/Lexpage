from django.urls import path
from django.views.generic.base import TemplateView

from .views import RegistrationView
from .views import ActivationView


# Registration based
urlpatterns = [
    path('register/', RegistrationView.as_view(), name='registration_register'),
    path('activate/complete/', TemplateView.as_view(template_name='profile/activation_complete.html'), name='registration_activation_complete'),
    path('activate/failed/', TemplateView.as_view(template_name='profile/activation_failed.html'), name='registration_activation_failed'),
    path('activate/', ActivationView.as_view(), name='registration_activate')
]


