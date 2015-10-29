from django import forms
from .models import Message
from profile.models import ActiveUser


class ReplyForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ReplyForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'rows': 5})

    class Meta:
        model = Message
        fields = ('text',)


class NewThreadForm(forms.Form):
    MAX_RECIPIENTS = 9

    title = forms.CharField(max_length=60, required=False, label='Sujet de la conversation', help_text='Si vous laissez ce champ vide, il sera complété automatiquement.')
    recipients = forms.CharField(max_length=100, label='Destinataires', help_text="Vous pouvez choisir jusqu'à %d destinataires, séparés par un espace." % MAX_RECIPIENTS)
    text = forms.CharField(label='Message', required=True, widget=forms.Textarea({'rows': 5}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(NewThreadForm, self).__init__(*args, **kwargs)
        self.fields['recipients'].widget.attrs.update({'class': 'username_complete'})

    def clean_recipients(self):
        recipients_raw = self.cleaned_data['recipients']
        recipients = []
        
        for recipient in set(recipients_raw.split(' ')): # Handle duplicates
            recipient = recipient.strip()
            try:
                if len(recipient) > 0:
                    user = ActiveUser.objects.all().get(username=recipient)
                    if user.get_username() == self.user.get_username():
                        raise forms.ValidationError('Vous ne devez pas vous inscrire dans les destinataires.')
                    else:
                        recipients.append(user)
            except ActiveUser.DoesNotExist:
                raise forms.ValidationError('Le nom d\'utilisateur %s est incorrect.' % str(recipient))
        
        # OK, so we now have a list of User objects...
        if not(1 <= len(recipients)):
            raise forms.ValidationError('Vous devez au moins choisir un destinataire.')
        if not(len(recipients) <= NewThreadForm.MAX_RECIPIENTS):
            raise forms.ValidationError('Vous ne pouvez entrer qu\'au maximum %d destinataires.' % NewThreadForm.MAX_RECIPIENTS)
        return recipients

