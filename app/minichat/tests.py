from django.core.urlresolvers import reverse
from django.test import TestCase
from minichat.models import Message
from django.contrib.auth.models import User


class ViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def test_archives(self):
        response = self.client.get(reverse('minichat_archives'))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse('minichat_archives'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_latests(self):
        response = self.client.get(reverse('minichat_latests'))
        self.assertEqual(response.status_code, 200)

    def test_post_login_required(self):
        url = reverse('minichat_post')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('auth_login') + '?next=' + url, 302, 200)

    def test_post_login(self):
        self.assertTrue(self.client.login(username='user1', password='user1'), 'I need to login for this test!')
        self.client.logout()

    def test_userslist_invalid(self):
        response = self.client.get(reverse('minichat_userslist'))
        self.assertEqual(response.status_code, 404)

    def test_userslist_smallquery(self):
        response = self.client.get(reverse('minichat_userslist'), {'query': 'a'})
        self.assertEqual(response.status_code, 404)

    def test_userslist(self):
        response = self.client.get(reverse('minichat_userslist'), {'query': 'abc'})
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
        anchored = self.users[:2]
        formats = [
            'Hello @{0} @{1}',
            '@{0}@{1}',
            '@{0}@{0}@{1}',
        ]
        for frmt in formats:
            message = Message(user=self.users[0], text=frmt.format(anchored[0].get_username(), anchored[1].get_username()))
            self.assertListEqual(message.parse_anchors(), anchored, msg='format: %s' % frmt)

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
        self.assertEqual(message.substitute().text, 'Hellp Wprld!')

    def test_empty_pattern(self):
        message = Message(user=self.author, text='s/o/')
        self.assertEqual(message.substitute().text, 'Hell Wrld!')

    def test_empty_match(self):
        message = Message(user=self.author, text='s//o')
        self.assertIsNone(message.substitute())

    def test_no_match(self):
        message = Message(user=self.author, text='s/bye/nothing')
        self.assertEqual(message.substitute().text, 'Hello World!')