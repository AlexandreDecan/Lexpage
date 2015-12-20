from django.conf.urls import url

from django.views.generic.base import TemplateView

from .views import RegistrationView
from .views import ActivationView


# Registration based
urlpatterns = [
                url(r'^register/$',
                    RegistrationView.as_view(),
                    name='registration_register'),
                url(r'^activate/complete/$',
                    TemplateView.as_view(template_name='profile/activation_complete.html'),
                    name='registration_activation_complete'),
                url(r'^activate/failed/$',
                    TemplateView.as_view(template_name='profile/activation_failed.html'),
                    name='registration_activation_failed'),
                url(r'^activate/$',
                    ActivationView.as_view(),
                    name='registration_activate')
]


