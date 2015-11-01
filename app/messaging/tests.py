from django.core.urlresolvers import reverse
from django.test import TestCase
from messaging.models import Thread
from profile.models import ActiveUser


class PostsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.user = ActiveUser.objects.filter(username='user1')[0]

        # Create a new conversation
        self.mbox = Thread.objects.create_thread(self.user, 'Hello World!', 'Hello World!', ActiveUser.objects.filter(username='admin'))
        self.thread = self.mbox.thread

        self.client.login(username='user1', password='user1')

    def setDown(self):
        self.thread.delete()

    def test_lists(self):
        for url in ['messaging_inbox', 'messaging_archived']:
            response = self.client.get(reverse(url))
            self.assertEqual(response.status_code, 200)

    def test_create(self):
        response = self.client.get(reverse('messaging_create'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('messaging_create', kwargs={'username': self.user}))
        self.assertEqual(response.status_code, 200)

    def test_show(self):
        url = reverse('messaging_show', kwargs={'thread': self.thread.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_reply(self):
        url = reverse('messaging_reply', kwargs={'thread': self.thread.pk})
        response = self.client.post(url, {'text': 'Hello New World!'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.thread = Thread.objects.get(pk=self.thread.pk)
        self.assertEqual(self.thread.last_message.text, 'Hello New World!')

    def test_mark(self):
        url = reverse('messaging_mark_read', kwargs={'thread': self.thread.pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_unmark(self):
        url = reverse('messaging_mark_unread', kwargs={'thread': self.thread.pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

