from django import forms
from .models import Season

class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        exclude = ('author', 'slug')

