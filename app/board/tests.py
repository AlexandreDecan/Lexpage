from django.core.urlresolvers import reverse
from django.test import TestCase
from board.models import Thread, Message
from blog.models import BlogPost
from profile.models import ActiveUser


class ThreadViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.assertTrue(self.client.login(username='user1', password='user1'), 'I need to login as user1/user1')
        self.threads = Thread.objects.filter(number__gt=10)
        self.assertTrue(len(self.threads) > 0, 'No thread with enough messages')

    def test_threadlist(self):
        urls = [
            'board_latests',
            'board_archives',
            'board_archives_messages',
            'board_followed',
            'board_followed_unread',
        ]
        for url in urls:
            response = self.client.get(reverse(url))
            self.assertEqual(response.status_code, 200, url)

    def test_threadcreate(self):
        response = self.client.get(reverse('board_create'))
        self.assertEqual(response.status_code, 200)

    def test_threadcreateforpost(self):
        post = BlogPost.published.latest()
        url = reverse('board_create_for_post', kwargs={'post': post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_threadrss(self):
        response = self.client.get(reverse('board_rss'))
        self.assertEqual(response.status_code, 200)

    def test_threadshow(self):
        urls = [
            'board_thread_show',
            'board_thread_show_last',
            'board_thread_show_unread',
        ]
        for url in urls:
            reversed_url = reverse(url, kwargs={'thread': self.threads[0].pk})
            response = self.client.get(reversed_url, follow=True)
            self.assertEqual(response.status_code, 200, url)

    def test_threadreply(self):
        url = reverse('board_thread_reply', kwargs={'thread': self.threads[0].pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_threadmarkunread(self):
        url = reverse('board_thread_mark_unread', kwargs={'thread': self.threads[0].pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)


class MesageViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.assertTrue(self.client.login(username='user1', password='user1'), 'I need to login as user1/user1')
        self.messages = Message.objects.filter(author=ActiveUser.objects.filter(username='user1'))
        self.assertTrue(len(self.messages) > 0, 'I need at least one message posted by user1/user1.')

    def test_messageshow(self):
        url = reverse('board_message_show', kwargs={'message': self.messages[0].pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_messageedit(self):
        url = reverse('board_message_edit', kwargs={'message': self.messages[0].pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_markunread(self):
        url = reverse('board_message_mark_unread', kwargs={'message': self.messages[0].pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_raw(self):
        url = reverse('board_message_raw', kwargs={'message': self.messages[0].pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)