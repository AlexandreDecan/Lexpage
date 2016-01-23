import os
from django.core.urlresolvers import reverse

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib import messages
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.views import login as view_login
from django.contrib.auth import authenticate, login

from notifications.models import Notification

from .forms import RegistrationForm, LoginForm, ChangeProfileForm, user_fields, profile_fields, ActivationForm
from .models import ActivationKey, Profile, ActiveUser


class ProfileChangeView(FormView):
    form_class = ChangeProfileForm
    template_name = 'profile/profile_edit.html'

    dispatch = method_decorator(login_required)(FormView.dispatch)

    def get_initial(self):
        initial = {}
        user = self.request.user
        for field in user_fields:
            initial[field] = getattr(user, field)

        profile = Profile.objects.get(user=user)
        for field in profile_fields:
            initial[field] = getattr(profile, field)

        return initial

    def form_valid(self, form):
        user = self.request.user
        profile = Profile.objects.get(user=user)

        for field in user_fields:
            setattr(user, field, form.cleaned_data[field])
        for field in profile_fields:
            setattr(profile, field, form.cleaned_data[field])

        # Uploaded avatar handling
        if form.cleaned_data['avatar_file']:
            image_file = form.cleaned_data['avatar_file']
            file_relative_path = os.path.join('images', 'avatars', self.request.user.get_username()+'.upload')
            file_local_path = os.path.join(settings.STATIC_ROOT, file_relative_path)

            new_file = open(file_local_path, 'wb')
            for chunk in image_file.chunks():
                new_file.write(chunk)
            new_file.close()
            profile.avatar = 'http://' + settings.ALLOWED_HOSTS[0] + os.path.join(settings.STATIC_URL, file_relative_path)

        user.save()
        profile.save()

        messages.success(self.request, 'Les informations de votre profil ont été mises à jour.')
        return redirect('profile_edit')


class ProfileShowView(TemplateView):
    template_name = 'profile/profile_show.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileShowView, self).get_context_data(**kwargs)
        user = get_object_or_404(ActiveUser, username=kwargs['username'])

        context['profile'] = user

        return context


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'profile/login.html'
    http_method_names = ['get', 'post']

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        remember_me = form.cleaned_data['remember_me']
        incognito = form.cleaned_data['incognito']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(self.request, user)
                # Handle pre-v4 account
                if user.password[0:3] == 'md5':
                    user.set_password(self.request.POST.get('password'))
                    user.save()
                if not remember_me:
                    self.request.session.set_expiry(0)
                self.request.session['incognito'] = incognito
                messages.success(self.request, 'Bienvenue %s !' % user.get_username())
        return view_login(self.request)


class ProfileListView(ListView):
    model = ActiveUser
    template_name = 'profile/profile_list.html'
    context_object_name = 'user_list'
    paginate_by = 25
    paginate_orphans = 5


class RegistrationView(FormView):
    form_class = RegistrationForm
    template_name = 'profile/registration_form.html'

    def dispatch(self, *args, **kwargs):
        # Remove expired activation keys
        ActivationKey.objects.delete_expired()

        return FormView.dispatch(self, *args, **kwargs)

    def form_valid(self, form):
        # Create new user
        username, email, password = form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password1']
        new_user, new_key = ActivationKey.objects.create_inactive_user(username, email, password)

        # Send email
        context = new_key.send_activation_email()

        return render(self.request, 'profile/registration_complete.html', context)


class ActivationView(FormView):
    form_class = ActivationForm
    template_name = 'profile/activation_confirm.html'

    def form_valid(self, form):
        key = form.cleaned_data['key']
        activated_user = ActivationKey.objects.activate_user(key)

        if activated_user:
            # TODO: Handle this notification using a pre_save signal, comparing new and old value of user.is_active
            Notification.objects.get_or_create(
                recipient=activated_user,
                title='Bienvenue sur Lexpage',
                description='Bienvenue sur Lexpage. Pensez à compléter votre profil et à choisir un avatar !',
                action=reverse('profile_edit'),
                app='profile',
                key='new')
            return redirect('registration_activation_complete')
        else:
            return redirect('registration_activation_failed')

