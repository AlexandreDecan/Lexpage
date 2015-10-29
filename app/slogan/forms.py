from django import forms
from .models import Slogan


class SloganAddForm(forms.ModelForm):
    
    class Meta:
        model = Slogan
        fields = ('slogan',)
