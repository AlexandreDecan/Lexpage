from django.test import TestCase
from django.core.urlresolvers import reverse
from notifications.models import Notification
from django.contrib.auth.models import User

class NotificationTests(TestCase):
    fixtures = ['devel']

    def test_dismiss_notification_logged_out(self):
        """A logged out user can not dismiss a notification"""
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 1)
        response = self.client.get(reverse('notification_dismiss', kwargs={'pk': notifications[0].id}))
        self.assertEqual(response.status_code, 302)
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 1)

    def test_dismiss_notification_logged_in(self):
        self.client.login(username='user1', password='user1')
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 1)
        notification_id = notifications[0].id
        response = self.client.get(reverse('notification_dismiss', kwargs={'pk': notification_id}))
        self.assertEqual(response.status_code, 200)
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 0)
        response = self.client.get(reverse('notification_dismiss', kwargs={'pk': notification_id}))
        self.assertEqual(response.status_code, 404)

    def test_dismiss_notification_other_user(self):
        User.objects.create_user(
            username='user2', email='user2@example.com', password='top_secret')
        self.client.login(username='user2', password='top_secret')
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 1)
        response = self.client.get(reverse('notification_dismiss', kwargs={'pk': notifications[0].id}))
        self.assertEqual(response.status_code, 404)
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 1)

    def test_repr_notification(self):
        notification = Notification.objects.get(recipient=User.objects.get(username='user1'))
        self.assertEqual(str(notification), '[user1] Nouvelle conversation')

    def test_dismiss_notification_by_showing(self):
        self.client.login(username='user1', password='user1')
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 1)
        notification_id = notifications[0].id
        response = self.client.get(reverse('notification_show', kwargs={'pk': notification_id}))
        self.assertEqual(response.status_code, 302)
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 0)
