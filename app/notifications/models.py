from django.db import models
from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from django.db.utils import IntegrityError


class UniqueNotificationManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        """
        Create Notifications and silently ignore database integrity errors
        (caused by failed unique constraints).

        Returns the created notifications
        """

        recipients = kwargs.pop('recipients')
        if not hasattr(recipients, '__iter__'):
            recipients = [recipients]

        notifications = []
        for recipient in recipients:
            parameters = dict(kwargs)
            parameters['recipient'] = recipient
            try:
                new_notification = self.model(**parameters)
                new_notification.save()
                notifications.append(new_notification)

            except IntegrityError: # Unique constraint failed
                pass
        return notifications


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
    description = models.CharField(verbose_name='Description', max_length=255, blank=True, default='')
    action = models.CharField(verbose_name='Action', max_length=255, blank=True, default='')
    recipient = models.ForeignKey(User, verbose_name='Destinataire')
    app = models.CharField(verbose_name='Application', max_length=50)
    key = models.CharField(verbose_name='Clé', max_length=100)
    date = models.DateTimeField(verbose_name='Date', auto_now_add=True)

    objects = UniqueNotificationManager()

    def dismiss(self):
        self.delete()

    def icon(self):
        return Notification.ICON.get(self.app, 'fa-warning')

    def __str__(self):
        return '[%s] %s' % (self.recipient.get_username(), self.title)

    def show_url(self):
        if self.action:
            return reverse('notification_show', kwargs={'pk': self.id})

    def dismiss_url(self):
        return reverse('notification_api_dismiss', kwargs={'pk': self.id})

    class Meta:
        get_latest_by = 'date'
        ordering = ['date']
        unique_together = ('app', 'key', 'recipient')

