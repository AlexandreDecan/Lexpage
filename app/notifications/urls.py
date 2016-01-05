from django.conf.urls import url
from .views import DismissView, ShowView
from django.views.generic import TemplateView


urlpatterns = [
                url(r'^(?P<pk>\d+)/dismiss/$',
                    DismissView.as_view(),
                    name='notification_dismiss'),
                url(r'^(?P<pk>\d+)/show/$',
                    ShowView.as_view(),
                    name='notification_show'),
                url(r'navbar.html$',
                    TemplateView.as_view(template_name='notifications/navbar.html'),
                    name='notifications_dropdown'),
                url(r'button.html$',
                    TemplateView.as_view(template_name='notifications/navbar_button.html'),
                    name='notifications_button'),
]
