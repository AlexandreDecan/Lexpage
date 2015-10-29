from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, SetPasswordForm

from commons.widgets import DateTimePicker
from django import forms
from .models import Profile

from captcha.fields import ReCaptchaField

import datetime


user_fields = ['first_name', 'last_name', 'email']
profile_fields = ['gender', 'birthdate', 'country', 'city', 'website_name', 'website_url', 'avatar',]


class ActivationForm(forms.Form):
    key = forms.CharField(required=True, label='Clé d\'activation')


class MyPasswordChangeForm(PasswordChangeForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput,
                                    required=True,
                                    label='Nouveau mot de passe',
                                    min_length=8)


class MyPasswordSetForm(SetPasswordForm):
    new_password1 = forms.CharField(widget=forms.PasswordInput,
                                    required=True,
                                    label='Nouveau mot de passe',
                                    min_length=8)



class ChangeProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label='Prénom')
    last_name = forms.CharField(max_length=30, required=False, label='Nom',
                                help_text='Cette information ne sera pas affichée publiquement.')
    email = forms.EmailField(label='Adresse e-mail', required=True, 
                             help_text='Cette information ne sera pas affichée publiquement.')

    birthdate = forms.DateField(required=False, label='Date de naissance', 
                                widget=DateTimePicker(options={'format': 'DD/MM/YYYY', 'pickTime': False}))

    avatar_file = forms.ImageField(required=False, label='Envoyer un avatar depuis votre disque',
                                   help_text='Vous pouvez envoyer un avatar depuis votre disque. Il doit s\'agir d\'un fichier image, en .gif, .jpg ou .png et de moins de 120x120 pixels. Votre ancien avatar sera automatiquement effacé et remplacé par le nouvel avatar.')

    class Meta:
        model = Profile
        fields = user_fields + profile_fields + ['avatar_file']

    def clean_avatar_file(self):
        in_file = self.cleaned_data['avatar_file']

        if not in_file:
            return  # No file, no clean ^^
        try:
            extension = in_file.name.rsplit('.', 1)[-1]
        except IndexError:
            extension = None

        if not(extension in ['jpg', 'gif', 'png']):
            raise forms.ValidationError('Les seules extensions autorisées sont .jpg, .png et .gif.')
        else:
            self.cleaned_data['avatar_file_ext'] = extension

        from PIL import Image, ImageFileIO
        try:

            im = Image.open(ImageFileIO.ImageFileIO(in_file))
            width, height = im.size
            if (0 < width <= 120) and (0 < height <= 120):
                return self.cleaned_data['avatar_file']
            else:
                raise forms.ValidationError('L\'image doit faire moins de 120x120 pixels.')
        except Exception:
            raise forms.ValidationError('Une erreur est survenue lors de l\'analyse de votre image.')

    def clean_birthdate(self):
        if self.cleaned_data['birthdate']:
            if (self.cleaned_data['birthdate'] > datetime.date.today() - datetime.timedelta(365*5)) \
                    or (self.cleaned_data['birthdate'] < datetime.date.today() - datetime.timedelta(365*100)):
                raise forms.ValidationError('La date choisie n\'est pas cohérente.')
        return self.cleaned_data['birthdate']


class LoginForm(AuthenticationForm):
    remember_me = forms.BooleanField(initial=True, required=False, label='Rester connecté')
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'username_complete'})


class RegistrationForm(forms.Form):
    username = forms.RegexField(regex=r'^[\w.@+_-]+$',
                                min_length=3,
                                max_length=20, 
                                required=True,
                                label='Nom d\'utilisateur',
                                error_messages={'invalid': 'Ce champ ne peut contenir que des lettres, des nombres et les caractères @/./+/-/_.'})
    email = forms.EmailField(label='E-mail',
                             required=True)
    password1 = forms.CharField(widget=forms.PasswordInput,
                                required=True,
                                label='Mot de passe', 
                                min_length=8)
    password2 = forms.CharField(widget=forms.PasswordInput,
                                required=True,
                                label='Confirmation')
    captcha = ReCaptchaField(attrs={'theme': 'clean', 'lang': 'fr'})

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
        if existing.exists():
            raise forms.ValidationError('Ce nom d\'utilisateur est déjà utilisé.')
        else:
            return self.cleaned_data['username']

    def clean_email(self):
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError('Cette adresse e-mail est déjà utilisée.')
        return self.cleaned_data['email']

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError('Les mots de passe ne correspondent pas.')
        return self.cleaned_data
