from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    ICON = {
        'blog': 'fa-clipboard', 
        'messaging': 'fa-inbox',
        'board': 'fa-comments-o', 
        'profile': 'fa-user', 
        'slogan': 'fa-quote-right',
        'minichat': 'fa-at',

        'game': 'fa-gamepad',
        
        'info': 'fa-info',
        'warning': 'fa-warning',
        'danger': 'fa-minus-circle',
        'success': 'fa-check',
        'question': 'fa-question',
        'reminder': 'fa-bell'
    }

    title = models.CharField(verbose_name='Titre', max_length=100)
    description = models.CharField(verbose_name='Description', max_length=255, blank=True)
    action = models.CharField(verbose_name='Action', max_length=255, blank=True)
    recipient = models.ForeignKey(User, verbose_name='Destinataire')
    app = models.CharField(verbose_name='Application', max_length=50)
    key = models.CharField(verbose_name='Clé', max_length=100)
    date = models.DateTimeField(verbose_name='Date', auto_now_add=True)

    def dismiss(self):
        self.delete()

    def get_icon(self):
        return Notification.ICON.get(self.app, 'fa-warning')

    def __unicode__(self):
        return '[%s] %s' % (self.recipient.get_username(), self.title)

    class Meta:
        get_latest_by = 'date'
        ordering = ['date']

