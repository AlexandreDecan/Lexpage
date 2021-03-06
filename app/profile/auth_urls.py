from commons.context_processors import global_settings
from django.urls import reverse_lazy, path, re_path

from django.contrib.auth import views as auth_views
from .views import LoginView

from .forms import MyPasswordChangeForm, MyPasswordSetForm

# Auth based
urlpatterns = [
    path('login/', LoginView.as_view(), name='auth_login'),
    path('logout/', auth_views.logout, {'template_name': 'profile/logout.html'}, name='auth_logout'),
    path('password/change/', auth_views.password_change, {
        'template_name': 'profile/password_change.html',
        'post_change_redirect': reverse_lazy('auth_password_change_done'),
        'password_change_form': MyPasswordChangeForm
    }, name='auth_password_change'),
    path('password/change/done/', auth_views.password_change_done, {'template_name': 'profile/password_change_done.html'}, name='auth_password_change_done'),
    path('password/reset/', auth_views.password_reset, {
        'template_name': 'profile/password_reset.html',
         'post_reset_redirect': reverse_lazy('auth_login'),
         'extra_context': {'password_reset':True},
         'email_template_name': 'profile/password_reset_email.txt',
         'subject_template_name': 'profile/password_reset_subject.txt',
         'extra_email_context': global_settings()
    }, name='auth_password_reset'),
    re_path(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.password_reset_confirm, {
        'template_name': 'profile/password_reset_confirm.html',
        'post_reset_redirect': reverse_lazy('auth_password_reset_complete'),
        'set_password_form': MyPasswordSetForm
    }, name='auth_password_reset_confirm'),
    path('password/reset/done/', auth_views.password_reset_complete, {'template_name': 'profile/password_reset_complete.html'}, name='auth_password_reset_complete'),
]
