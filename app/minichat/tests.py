from datetime import timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.lorem_ipsum import words
from minichat.models import Message
from notifications.models import Notification
from rest_framework.test import APITestCase


class ViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def test_archives(self):
        response = self.client.get(reverse('minichat_archives'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('minichat_archives'), follow=True)
        self.assertEqual(response.status_code, 200)


class AnchorTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.users = User.objects.all()

    def test_single(self):
        anchored = self.users[1]
        formats = [
            'Hello @{}!',
            'Hello@{}!',
            '@{}',
            '@@{}',
            '@{}@',
        ]
        for frmt in formats:
            message = Message(user=self.users[0], text=frmt.format(anchored.get_username()))
            self.assertListEqual(message.parse_anchors(), [anchored], msg='format: %s' % frmt)

    def test_multiple(self):
        formats = [
            'Hello @{0} @{1}',
            '@{0}@{1}',
            '@{0}@{0}@{1}',
        ]
        for frmt in formats:
            message = Message(user=self.users[0], text=frmt.format(self.users[0].get_username(), self.users[1].get_username()))
            self.assertListEqual(message.parse_anchors(), [self.users[0], self.users[1]], msg='format: %s' % frmt)

    def test_invalid(self):
        anchored = self.users[:2]
        formats = [
            '@{0}abcdefghijklmnopqrstuvwxyz', # ... and expect this is not a valid username
            '@ {0}',
        ]
        for frmt in formats:
            message = Message(user=self.users[0], text=frmt.format(anchored[0].get_username(), anchored[1].get_username()))
            self.assertListEqual(message.parse_anchors(), [], msg='format: %s' % frmt)


class SubstituteTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.users = User.objects.all()
        self.author = self.users[0]
        Message(user=self.author, text='Older message').save()
        Message(user=self.author, text='Hello World!').save()

    def test_no_message(self):
        message = Message(user=self.users[1], text='s/nothing/todo')
        self.assertIsNone(message.substitute())

    def test_message_selection(self):
        # Create new message from another author
        other_message = Message(user=self.users[1], text='Another message')
        other_message.save()

        message = Message(user=self.author, text='s/nothing/todo')
        modified = message.substitute()

        self.assertEqual(modified.user, self.author)
        self.assertEqual(modified.text, 'Hello World!')

        # Remove the other message
        other_message.delete()

    def test_valid_substitution(self):
        message = Message(user=self.author, text='s/World!/Universe!?')
        self.assertEqual(message.substitute().text, 'Hello Universe!?')

    def test_valid_multiple_substitutions(self):
        message = Message(user=self.author, text='s/o/p')
        self.assertEqual(message.substitute().text, 'Hellp World!')

    def test_empty_pattern(self):
        message = Message(user=self.author, text='s/o/')
        self.assertEqual(message.substitute().text, 'Hell World!')

    def test_empty_match(self):
        message = Message(user=self.author, text='s//o')
        self.assertIsNone(message.substitute())

    def test_no_match(self):
        message = Message(user=self.author, text='s/bye/nothing')
        self.assertEqual(message.substitute().text, 'Hello World!')


class ApiTests(APITestCase):
    fixtures = ['devel']

    def setUp(self):
        self.users = User.objects.all()
        self.author = self.users[0]

    def test_post_login_required(self):
        url = reverse('minichat_post')
        response = self.client.post(url, {'text': 'foo'})
        self.assertEqual(response.status_code, 403)

    def test_unallowed_methods(self):
        """ Get Delete and Put are not allowed """
        self.client.login(username='user1', password='user1')
        for method in ('get', 'put', 'delete', 'patch'):
            response = getattr(self.client, method)(reverse('minichat_post'))
            self.assertEqual(response.status_code, 405)

    def test_old_message_cant_be_modified(self):
        self.client.login(username='user1', password='user1')
        Message.objects.all().delete()
        self.assertEqual(len(Message.objects.all()), 0)
        response = self.client.post(reverse('minichat_post'), {'text': 'Hello World!'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['text'], 'Hello World!')
        self.assertEqual(len(Message.objects.all()), 1)

        latest_message = Message.objects.latest()
        latest_message.date = latest_message.date - timedelta(minutes=6)
        latest_message.save()

        response = self.client.post(reverse('minichat_post'), {'text': 's/hello/world'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(Message.objects.all()), 1)
        latest_message.refresh_from_db()
        self.assertEqual(latest_message.text, 'Hello World!')

    def test_substitute(self):
        self.client.login(username='user1', password='user1')
        response = self.client.post(reverse('minichat_post'), {'text': 'Hello World!'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['text'], 'Hello World!')
        self.assertEqual(Message.objects.last().text, 'Hello World!')
        response = self.client.post(reverse('minichat_post'), {'text': 's/World/John'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.last().text, 'Hello John!')
        self.client.logout()

    def test_notifications_after_message_update(self):
        users = [
            User.objects.create_user(username=username, email='%s@example.com' % username, password=username)
            for username in ('fake1', 'fake2', 'fake3')
        ]
        for user in users:
            user.save()
        self.client.login(username='user1', password='user1')
        Notification.objects.all().delete()

        response = self.client.post(reverse('minichat_post'), {'text': 'hello @fake1 @fake2'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(Notification.objects.all()), 2)

        response = self.client.post(reverse('minichat_post'), {'text': 's/hello/world'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Notification.objects.all()), 2)

        # Check that fake1 and fake2 have a notification with NEW text
        self.assertIn('world', Notification.objects.get(recipient=users[0]).description)
        self.assertIn('world', Notification.objects.get(recipient=users[1]).description)

        response = self.client.post(reverse('minichat_post'), {'text': 's/@fake1/@fake3'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Notification.objects.all()), 2)

        # Check that fake1 has no notification
        self.assertEqual(len(Notification.objects.filter(recipient=users[0])), 0)

        # Check that fake2 has a notification with NEW text
        self.assertIn('world', Notification.objects.get(recipient=users[1]).description)

        # Check that fake3 has a notification
        self.assertIn('world', Notification.objects.get(recipient=users[2]).description)

    def test_multiple_notifications(self):
        for username in ('user2', 'user3'):
            User.objects.create_user(
                username=username, email='%s@example.com' % username, password='top_secret')
        Notification.objects.all().delete()
        self.assertEqual(len(Notification.objects.all()), 0)
        self.client.login(username='user1', password='user1')
        response = self.client.post(reverse('minichat_post'), {'text': '@admin hello @user2 @user3'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['text'], '@admin hello @user2 @user3')
        self.assertEqual(Message.objects.last().text, '@admin hello @user2 @user3')
        self.assertEqual(len(Notification.objects.all()), 3)
        self.client.logout()

    def test_post_login(self):
        self.client.login(username='user1', password='user1')
        response = self.client.post(reverse('minichat_post'), {'text': 'Hello World!'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['text'], 'Hello World!')
        self.assertEqual(Message.objects.last().text, 'Hello World!')
        self.client.logout()

    def test_latest_minichat(self):
        Message.objects.all().delete()
        for i in range(0,57):
            Message(user=self.author, text=words(5, False)).save()
        Message(user=self.author, text='Last message').save()

        response = self.client.get(reverse('minichat-api-latest-list'), format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 58)
        self.assertEqual(len(response.data['results']), 20)

        first_message = response.data['results'][0]
        # Striclty check the fields to avoir extra disclosure (field id is not sent)
        self.assertEqual(set(first_message.keys()), {'user', 'text', 'date'})

        # Striclty check the fields to avoir extra disclosure (we should only send username
        # and profile, not password, email, ...)
        self.assertEqual(set(first_message['user'].keys()), {'username', 'profile', 'get_absolute_url'})


        # Striclty check the fields to avoir extra disclosure (we should only send avatar,
        # not last_visit, ...)
        self.assertEqual(set(first_message['user']['profile'].keys()), {'avatar'})

        self.assertEqual(first_message['text'], 'Last message')


class MinichatCachingTests(APITestCase):
    def setUp(self):
        cache.clear()

        self.url = reverse('minichat-api-latest-list')

        # First response should return an etag
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.has_header('ETag'))
        self.etag = response['ETag']

    def test_missing_etag(self):
        """
        A request with a missing ETag should lead to a 200 with the same ETag.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.etag, response['ETag'])

    def test_invalid_etag(self):
        """
        A request with an invalid ETag should lead to a 200 with the same ETag.
        """
        response = self.client.get(self.url, HTTP_IF_NONE_MATCH='blablabla')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.etag, response['ETag'])

    def test_valid_etag(self):
        """
        A request with a valid existing ETag should lead to a 304.
        """
        response = self.client.get(self.url, HTTP_IF_NONE_MATCH=self.etag)
        self.assertEqual(response.status_code, 304)
        self.assertEqual(self.etag, response['ETag'])

    def test_etag_renewal(self):
        """
        An ETag should be invalidated if a new message is posted on the minichat, or edited, or deleted.
        """
        user = User.objects.create_user(username='user1', email='user1@example.com', password='user1')

        # After new message
        message = Message.objects.create(user=user, text='Hello world')
        response = self.client.get(self.url, HTTP_IF_NONE_MATCH=self.etag)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.etag, response['ETag'])
        new_etag = response['ETag']

        # After modification
        message.text = 'Hello universe'
        message.save()
        response = self.client.get(self.url, HTTP_IF_NONE_MATCH=self.etag)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.etag, response['ETag'])
        self.assertNotEqual(new_etag, response['ETag'])
        new_etag = response['ETag']

        # After deletion
        message.delete()
        response = self.client.get(self.url, HTTP_IF_NONE_MATCH=self.etag)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.etag, response['ETag'])
        self.assertNotEqual(new_etag, response['ETag'])
