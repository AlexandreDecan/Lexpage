from commons.context_processors import global_settings
from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.template.loader import render_to_string
from notifications.models import Notification
import datetime


class Command(NoArgsCommand):
    help = "Send a mail notification for (unread) pending notifications."

    # A mail will be sent only if there exists a pending notification
    # that is older than min_delay and younger than max_delay
    min_delay = datetime.timedelta(days=2)
    max_delay = datetime.timedelta(days=3)

    # We assume that cron calls this task only once per hour, on a 
    # fixed basis. task_hours stores the hours at which a mail could be 
    # sent. 
    task_hours = [12]

    def send_mail_notification(self, user):
        """
        Send a mail to the user with a list of its pending notifications. 
        """

        # Get its notifications
        notifications = Notification.objects.filter(recipient=user)

        # Render the mail template
        context = {'user': user, 
                    'notifications': notifications}
        context.update(global_settings())

        subject = render_to_string('notifications/mail_subject.txt', context)
        text = render_to_string('notifications/mail_content.txt', context)

        # Send it!
        # print 'user: %s\nsubject: %s\ntext: %s' % (user.username, subject, text)
        if user.email:
          user.email_user(subject, text, settings.DEFAULT_FROM_EMAIL)
          print('Mail sent to %s (%s)' % (user.username, user.email))

    def handle_noargs(self, **options):
        # Check if current hour is in task_hours. If not, stop. 
        if not (datetime.datetime.now().hour in Command.task_hours):
            return

        print('Task: notifications by mail.')
        
        min_date = datetime.datetime.now() - Command.min_delay
        max_date = datetime.datetime.now() - Command.max_delay

        # Retrieve the list of pending notifications
        notifications = Notification.objects.filter(date__gte=max_date, date__lt=min_date)
        users = set()

        # Get a list of users to warn. 
        for notification in notifications:
            users.add(notification.recipient)

        # Send a mail to each user. 
        for user in users:
            self.send_mail_notification(user)

        return
