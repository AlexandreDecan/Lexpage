import time
from django.core.urlresolvers import reverse
from django.test import TestCase
from minichat.models import Message
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.utils.lorem_ipsum import words
from tests_helpers import LexpageTestCase, logged_in_test, SELENIUM_AVAILABLE, without_redis
from datetime import date, timedelta
from django.contrib.humanize.templatetags.humanize import naturalday

if SELENIUM_AVAILABLE:
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.common.exceptions import NoSuchElementException

from notifications.models import Notification



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
        self.assertEqual(response.data['anchors'], [])
        self.assertEqual(Message.objects.last().text, 'Hello World!')
        response = self.client.post(reverse('minichat_post'), {'text': 's/World/John'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['anchors'], [])
        self.assertEqual(Message.objects.last().text, 'Hello John!')
        self.client.logout()

    def test_anchor(self):
        Notification.objects.all().delete()
        self.assertEqual(len(Notification.objects.all()), 0)
        self.client.login(username='user1', password='user1')
        response = self.client.post(reverse('minichat_post'), {'text': '@admin hello'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['text'], '@admin hello')
        self.assertEqual(response.data['anchors'], ['admin'])
        self.assertEqual(Message.objects.last().text, '@admin hello')
        self.assertEqual(len(Notification.objects.all()), 1)
        self.client.logout()

    def test_anchor_not_recreated_after_updating_message(self):
        Notification.objects.all().delete()
        self.assertEqual(len(Notification.objects.all()), 0)
        self.client.login(username='user1', password='user1')
        response = self.client.post(reverse('minichat_post'), {'text': '@admin hello'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(Notification.objects.all()), 1)
        Notification.objects.all().delete()
        self.assertEqual(len(Notification.objects.all()), 0)
        response = self.client.post(reverse('minichat_post'), {'text': 's/hello/world'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['text'], 's/hello/world')
        self.assertEqual(response.data['anchors'], [])
        self.assertEqual(Message.objects.last().text, '@admin world')
        self.assertEqual(len(Notification.objects.all()), 0)
        self.client.logout()


    def test_anchor_deleted_after_updating_message(self):
        Notification.objects.all().delete()
        self.assertEqual(len(Notification.objects.all()), 0)
        self.client.login(username='user1', password='user1')
        response = self.client.post(reverse('minichat_post'), {'text': '@admin hello'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(Notification.objects.all()), 1)
        response = self.client.post(reverse('minichat_post'), {'text': 's/@admin/nobody'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['text'], 's/@admin/nobody')
        self.assertEqual(response.data['anchors'], [])
        self.assertEqual(Message.objects.last().text, 'nobody hello')
        self.assertEqual(len(Notification.objects.all()), 0)
        self.client.logout()


    def test_anchor_created_after_updating_message(self):
        Notification.objects.all().delete()
        self.assertEqual(len(Notification.objects.all()), 0)
        self.client.login(username='user1', password='user1')
        response = self.client.post(reverse('minichat_post'), {'text': 'admin hello'})
        self.assertEqual(response.status_code, 201)
        response = self.client.post(reverse('minichat_post'), {'text': 's/a/@a'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['text'], 's/a/@a')
        self.assertEqual(response.data['anchors'], ['admin'])
        self.assertEqual(Message.objects.last().text, '@admin hello')
        self.assertEqual(len(Notification.objects.all()), 1)
        self.client.logout()


    def test_anchor_updated_after_updating_message(self):
        Notification.objects.all().delete()
        self.assertEqual(len(Notification.objects.all()), 0)
        self.client.login(username='user1', password='user1')
        response = self.client.post(reverse('minichat_post'), {'text': '@admin hello'})
        self.assertEqual(response.status_code, 201)
        response = self.client.post(reverse('minichat_post'), {'text': 's/hello/@user1 world'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['text'], 's/hello/@user1 world')
        self.assertEqual(response.data['anchors'], ['user1'])
        self.assertEqual(Message.objects.last().text, '@admin @user1 world')
        self.assertEqual(len(Notification.objects.all()), 2)
        self.client.logout()


    def test_multiple_anchors(self):
        for username in ('user2', 'user3'):
            User.objects.create_user(
                username=username, email='%s@example.com' % username, password='top_secret')
        Notification.objects.all().delete()
        self.assertEqual(len(Notification.objects.all()), 0)
        self.client.login(username='user1', password='user1')
        response = self.client.post(reverse('minichat_post'), {'text': '@admin hello @user2 @user3'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['text'], '@admin hello @user2 @user3')
        self.assertEqual(response.data['anchors'], ['admin', 'user2', 'user3'])
        self.assertEqual(Message.objects.last().text, '@admin hello @user2 @user3')
        self.assertEqual(len(Notification.objects.all()), 3)
        self.client.logout()

    def test_post_login(self):
        self.client.login(username='user1', password='user1')
        response = self.client.post(reverse('minichat_post'), {'text': 'Hello World!'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['text'], 'Hello World!')
        self.assertEqual(response.data['anchors'], [])
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
        self.assertEqual(list(first_message.keys()), ['user', 'text', 'date'])

        # Striclty check the fields to avoir extra disclosure (we should only send username
        # and profile, not password, email, ...)
        self.assertEqual(list(first_message['user'].keys()), ['username', 'profile', 'get_absolute_url'])


        # Striclty check the fields to avoir extra disclosure (we should only send avatar,
        # not last_visit, ...)
        self.assertEqual(list(first_message['user']['profile'].keys()), ['avatar'])

        self.assertEqual(first_message['text'], 'Last message')

    def test_smiley(self):
        Message(user=self.author, text='je suis content :-)').save()

        response = self.client.get(reverse('minichat-api-latest-list'), format='json')

        self.assertEqual(response.status_code, 200)

        first_message = response.data['results'][0]
        self.assertEqual(first_message['text'], 'je suis content <img src="/static/images/smiley/smile.gif"/>')

    def test_url(self):
        Message(user=self.author, text='trop fort http://lexpage.net').save()

        response = self.client.get(reverse('minichat-api-latest-list'), format='json')
        formatted_url = '<a href="http://lexpage.net" title="http://lexpage.net" data-toggle="tooltip" data-placement="top" data-container="body" class="fa fa-external-link" rel="nofollow"></a>'

        self.assertEqual(response.status_code, 200)

        first_message = response.data['results'][0]
        self.assertEqual(first_message['text'], 'trop fort %s' % formatted_url)

class TemplateTestCase(LexpageTestCase):

    def test_natural_date_invalid_date(self):
        self.selenium.get(self.live_server_url)
        filter_invalid_date = self.selenium.execute_script('return env.getFilter("naturalDay")("foo");');
        self.assertEqual(filter_invalid_date, 'Invalid date')

    def test_natural_date_django_equivalent(self):
        self.selenium.get(self.live_server_url)
        # One year and 30 days
        for i in range(0, 365+30):
            time.sleep(0.1)
            d = date.today() - timedelta(days=i)
            formatted_date = d.isoformat()
            filter_date = self.selenium.execute_script('return env.getFilter("naturalDay")("%s");' % formatted_date);
            self.assertEqual(filter_date, naturalday(d, 'l j b.'))

class MinichatBrowserTest(LexpageTestCase):
    fixtures = ['devel']

    def setUp(self):
        self.users = User.objects.all()
        self.author = self.users[0]
        super().setUp()

    def post_message(self, timeout=5, text_message='Hello World'):
        text_message_xpath = '//div[@class="minichat-text" and text()[contains(.,"%s")]]' % text_message
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(text_message_xpath)
        time.sleep(1)
        Message(user=self.author, text=text_message).save()
        WebDriverWait(self.selenium, timeout).until(
            lambda driver: driver.find_element_by_xpath(text_message_xpath))

    @logged_in_test()
    def test_minichat_message(self):
        self.post_message()

    @without_redis()
    @logged_in_test()
    def test_minichat_message_without_redis(self):
        """Without redis, a message takes up to 30 seconds to get printed"""
        text_message = 'Je suis un test'
        text_message_xpath = '//div[@class="minichat-text" and text()[contains(.,"%s")]]' % text_message
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(text_message_xpath)
        time.sleep(1)
        Message(user=self.author, text=text_message).save()
        time.sleep(15)
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(text_message_xpath)
        WebDriverWait(self.selenium, 20).until(
            lambda driver: driver.find_element_by_xpath(text_message_xpath))

    @logged_in_test()
    def test_minichat_is_not_reloaded_with_websockets(self):
        """This test will ensure that the minichat is not reloaded with websockets
        if there are no new messages"""
        self.post_message()
        # At this point the minichat should not be updated anymore
        # We will replace it with something else and wait.
        placeholder = '<h2>Bob! T\'as mis ou le minichat?</h2>'
        self.selenium.execute_script('$(minichat_content).html("%s");' % placeholder);
        minichat_html = lambda: self.selenium.execute_script('return $(minichat_content).html();')
        self.assertEqual(minichat_html(), placeholder)
        time.sleep(3*30+1) # Wait 3 refresh interval + 1s
        self.assertEqual(minichat_html(), placeholder)

    @without_redis()
    @logged_in_test()
    def test_minichat_is_reloaded_without_websockets(self):
        """This test will ensure that the minichat is reloaded without websockets
        even if there are no new messages"""
        time.sleep(1)
        # At this point the minichat should be updated every 30 seconds
        # because redis is not started
        placeholder = '<h2>Bob! T\'as mis ou le minichat?</h2>'
        self.selenium.execute_script('$(minichat_content).html("%s");' % placeholder);
        minichat_html = lambda: self.selenium.execute_script('return $(minichat_content).html();')
        self.assertEqual(minichat_html(), placeholder)
        time.sleep(2*30+1) # Wait 2 refresh interval + 1s
        self.assertNotEqual(minichat_html(), placeholder)

