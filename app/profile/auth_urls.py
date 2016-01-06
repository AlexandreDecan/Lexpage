from django.conf.urls import url

from django.core.urlresolvers import reverse_lazy

from django.contrib.auth import views as auth_views
from .views import LoginView

from .forms import MyPasswordChangeForm, MyPasswordSetForm

# Auth based
urlpatterns = [
                url(r'^login/$',
                    LoginView.as_view(),
                    name='auth_login'),
                url(r'^logout/$',
                    auth_views.logout,
                    {'template_name': 'profile/logout.html'},
                    name='auth_logout'),
                url(r'^password/change/$',
                    auth_views.password_change,
                    {'template_name': 'profile/password_change.html',
                    'post_change_redirect': reverse_lazy('auth_password_change_done'),
                    'password_change_form': MyPasswordChangeForm},
                    name='auth_password_change'),
                url(r'^password/change/done/$',
                    auth_views.password_change_done,
                    {'template_name': 'profile/password_change_done.html'},
                    name='auth_password_change_done'),
                url(r'^password/reset/$',
                    auth_views.password_reset,
                    {'template_name': 'profile/password_reset.html',
                     'post_reset_redirect': reverse_lazy('auth_login'),
                     'extra_context': {'password_reset':True},
                     'email_template_name': 'profile/password_reset_email.txt',
                     'subject_template_name': 'profile/password_reset_subject.txt'},
                    name='auth_password_reset'),
                url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                    auth_views.password_reset_confirm,
                    {'template_name': 'profile/password_reset_confirm.html',
                     'post_reset_redirect': reverse_lazy('auth_password_reset_complete'),
                     'set_password_form': MyPasswordSetForm},
                    name='auth_password_reset_confirm'),
                url(r'^password/reset/done/$',
                    auth_views.password_reset_complete,
                    {'template_name': 'profile/password_reset_complete.html'},
                    name='auth_password_reset_complete'),
]
