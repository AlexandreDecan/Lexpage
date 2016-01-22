from django.core.urlresolvers import reverse
from django.test import TestCase
from board.models import Thread, Message
from blog.models import BlogPost
from profile.models import ActiveUser


class ThreadViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.client.login(username='user1', password='user1')
        self.threads = Thread.objects.filter(number__gt=10)

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
        nb_threads = Thread.objects.count()
        response = self.client.post(reverse('board_create'), {'title': 'Hello World!',
                                                              'text': 'Hello World!'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Thread.objects.count(), nb_threads + 1)

    def test_threadcreateforpost(self):
        post = BlogPost.published.latest()
        url = reverse('board_create_for_post', kwargs={'post': post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_threadpost(self):
        old_message = self.threads[0].last_message
        Message(author=ActiveUser.objects.get(username='user1'), thread=self.threads[0], text='Hello World!').save()
        self.threads[0].refresh_from_db()
        self.assertNotEqual(self.threads[0].last_message, old_message)

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

    def test_deletemessage(self):
        # Log as admin
        self.client.login(username='admin', password='admin')
        user = ActiveUser.objects.get(username='admin')

        # Create dummy thread
        thread = Thread(title='Hello World!')
        thread.save()
        msg1 = Message(author=user, thread=thread, text='Hello 1')
        msg2 = Message(author=user, thread=thread, text='Hello 2')
        msg1.save()
        msg2.save()

        thread.refresh_from_db()
        self.assertEqual(thread.number, 2)
        self.assertEqual(thread.last_message, msg2)

        # Remove second message
        response = self.client.get(reverse('board_message_delete', kwargs={'message': msg2.pk}), follow=True)
        self.assertEqual(response.status_code, 200)

        thread.refresh_from_db()

        self.assertEqual(thread.number, 1)
        self.assertEqual(thread.last_message, msg1)
        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(pk=msg2.pk)

        # Remove first (and last) message
        response = self.client.get(reverse('board_message_delete', kwargs={'message': msg1.pk}))
        self.assertRedirects(response, reverse('board_latests'))

        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(pk=msg1.pk)
        with self.assertRaises(Thread.DoesNotExist):
            Thread.objects.get(pk=thread.pk)


class MessageViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.client.login(username='user1', password='user1')
        self.messages = Message.objects.filter(author=ActiveUser.objects.filter(username='user1'))

    def test_messageshow(self):
        url = reverse('board_message_show', kwargs={'message': self.messages[0].pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_messageedit(self):
        message = self.messages[0]

        url = reverse('board_message_edit', kwargs={'message': message.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {'text': 'Hello World!'}, follow=True)
        message.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.text, 'Hello World!')

    def test_messagemoderate(self):
        message = self.messages[0]
        self.client.login(username='admin', password='admin')

        url = reverse('board_message_moderate', kwargs={'message': message.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {'text': 'Hello World!', 'moderated': True}, follow=True)
        message.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.text, 'Hello World!')
        self.assertEqual(message.moderated, True)

    def test_markunread(self):
        url = reverse('board_message_mark_unread', kwargs={'message': self.messages[0].pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)


class APITests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        user = ActiveUser.objects.get(username='admin')

        # Create dummy thread
        thread = Thread(title='Hello World!')
        thread.save()

        self.msg1 = Message(author=user, thread=thread, text='Hello 1')
        self.msg2 = Message(author=user, thread=thread, text='Hello 2')
        self.msg1.save()
        self.msg2.save()

    def test_message_detail(self):
        response = self.client.get(reverse('board_api_message-detail', kwargs={'pk': self.msg1.pk}), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['text'], 'Hello 1')
        self.assertEqual(response.data['author']['username'], 'admin')

    def test_invalid_message_detail(self):
        response = self.client.get(reverse('board_api_message-detail', kwargs={'pk': -1}), format='json')
        self.assertEqual(response.status_code, 404)

