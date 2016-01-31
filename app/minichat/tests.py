import time
from django.core.urlresolvers import reverse
from django.test import TestCase
from minichat.models import Message
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.utils.lorem_ipsum import words
from helpers.tests import LexpageTestCase, logged_in_test, SELENIUM_AVAILABLE, without_redis, sqlite_sleep
from datetime import date, timedelta
from django.contrib.humanize.templatetags.humanize import naturalday
from notifications.models import Notification

if SELENIUM_AVAILABLE:
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.common.exceptions import NoSuchElementException


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

    def test_natural_date_on_home_page(self):
        self.natural_date_django_equivalent(self.live_server_url)

    def test_natural_date_on_search_page(self):
        self.natural_date_django_equivalent('%s%s' % (self.live_server_url, reverse('search')))

    def natural_date_django_equivalent(self, url):
        self.selenium.get(url)
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
        text_message_xpath = '//div[@class="minichat-text"]/div[text()[contains(.,"%s")]]' % text_message
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
        text_message_xpath = '//div[@class="minichat-text"]/div[text()[contains(.,"%s")]]' % text_message
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

class MinichatNunjucksTest(LexpageTestCase):

    def setUp(self):
        # Running the tests just before midnight could cause failures
        if time.strftime("%H%M") in ['2358', '2359']: # pragma: no cover
            time.sleep(125)
        self.users = []
        for username in ('user1', 'user2', 'user3'):
            user = User.objects.create_user(
                username=username, email='%s@example.com' % username, password=username)
            user.save()
            sqlite_sleep(.5)
            self.users.append(user)

    def verify_minichat_groups(self, groups):
        """This fonction tests that messages in the minichat are splitted correctly between the
        groups in the current page.

        groups (list of a list): Content of the messages, as they should be shown on the page.
        """
        time.sleep(2)
        messages = self.selenium.find_elements_by_css_selector('.minichat-text')
        self.assertEqual(len(groups), len(messages))
        for message_group in messages:
            inner_messages = message_group.find_elements_by_xpath('./div')
            group = groups.pop(0)
            self.assertEqual(len(group), len(inner_messages))
            for inner_message in inner_messages:
                self.assertIn(group.pop(0), inner_message.text)

    def verify_minichat_read(self, expected_read, expected_unread):
        """This fonction tests that messages in the minichat are marked as read
        or unread as expected
        """
        all_messages = self.selenium.find_elements_by_css_selector('.minichat-text div')
        unread_messages = self.selenium.find_elements_by_css_selector('.minichat-text div.new')
        unread_messages_text = [e.text for e in unread_messages]
        read_messages_text = [e.text for e in all_messages if e.text not in unread_messages_text]
        for expected_messages, actual_messages in ((expected_read, read_messages_text),
                                                   (expected_unread, unread_messages_text),):
            self.assertEqual(len(expected_messages), len(actual_messages))
            all_messages_found = []
            for e in expected_messages:
                messages_found = [a for a in actual_messages if a.endswith(e)]
                self.assertEqual(len(messages_found), 1)
                all_messages_found += messages_found
            self.assertEqual(len(all_messages_found), len(list(set(all_messages_found))))

    @logged_in_test()
    def test_highlight(self):
        for input_text, number in [('coucou @user1', 1),
                            ('@user1', 1),
                            ('@user12', 0),
                            ('x @user1 x', 1),
                            ('@user1 coucou', 1),
                            ('@user1 @user1', 2),
                            ('@user1 @user2', 1),
                            ('@ @user1', 1),
                            ('@@user1', 1),
                            ('@@user2', 0),
                            ('@', 0),
                            ('no no no no', 0),
                            ('cool@user1.com', 1),
                            ('cucou@user12.com', 0),
                            ('coucou @user12', 0),
                            ('coucou @user12 salut', 0),
                            ('@user2', 0)]:
            Message.objects.all().delete()
            sqlite_sleep(.5)
            Message(user=self.users[1], text=input_text).save()
            time.sleep(1)
            nb_notifications = len(Notification.objects.filter(recipient=self.users[0]))
            if number > 0:
                self.assertEqual(nb_notifications, 1, 'A notification is not created for %s' % input_text)
            else:
                self.assertEqual(nb_notifications, 0, 'A notification is created for %s' % input_text)

            highlights = self.selenium.find_elements_by_css_selector('.minichat-text div strong')
            self.assertEqual(len(highlights), number, 'Test failed with %s' % input_text)

    def test_highlight_when_logged_out(self):
        self.selenium.get(self.live_server_url)
        for input_text, number in [('coucou @user1', 0),
                            ('@user1', 0),
                            ('@user1 @user1', 0),
                            ('@ @user1', 0),
                            ('@', 0),
                            ('no no no no', 0),
                            ('cucou@user12.com', 0),
                            ('coucou @user12 salut', 0),
                            ('@user2', 0)]:
            Message.objects.all().delete()
            sqlite_sleep(.5)
            Message(user=self.users[1], text=input_text).save()
            self.selenium.refresh()
            time.sleep(1)
            highlights = self.selenium.find_elements_by_css_selector('.minichat-text div strong')
            self.assertEqual(len(highlights), number, 'Test failed with %s' % input_text)

    @logged_in_test()
    def test_one_message_class(self):
        Message(user=self.users[0], text='Hello World!').save()
        self.verify_minichat_groups([['Hello World!']])

    @logged_in_test()
    def test_two_messages_class(self):
        Message(user=self.users[0], text='Hello World!').save()
        sqlite_sleep(.5)
        Message(user=self.users[0], text='Traduction: Bonjour').save()
        self.verify_minichat_groups([
            [
                'Hello World!',
                'Traduction: Bonjour',
            ],
        ])

    @logged_in_test()
    def test_three_messages_class(self):
        Message(user=self.users[0], text='Hello World!').save()
        sqlite_sleep(.5)
        Message(user=self.users[0], text='Traduction: Bonjour').save()
        sqlite_sleep(.5)
        Message(user=self.users[0], text='(en Anglais)').save()
        self.verify_minichat_groups([
            [
                'Hello World!',
                'Traduction: Bonjour',
                '(en Anglais)',
            ],
        ])

    @logged_in_test()
    def test_three_messages_different_users(self):
        Message(user=self.users[0], text='Hello World!').save()
        sqlite_sleep(.5)
        Message(user=self.users[1], text='Traduction: Bonjour').save()
        sqlite_sleep(.5)
        Message(user=self.users[2], text='(en Anglais)').save()
        self.verify_minichat_groups([
            [ '(en Anglais)', ],
            [ 'Traduction: Bonjour', ],
            [ 'Hello World!', ],
        ])

    @logged_in_test(incognito=False)
    def test_conversation(self):
        self.selenium.refresh()
        Message(user=self.users[0], text='Hello You').save()
        sqlite_sleep(.5)
        self.verify_minichat_groups([
            ['Hello You'],
        ])
        self.verify_minichat_read(['Hello You'], [])
        Message(user=self.users[1], text='Yes').save()
        sqlite_sleep(.5)
        self.verify_minichat_groups([
            ['Yes'],
            ['Hello You'],
        ])
        self.verify_minichat_read(['Hello You'], ['Yes'])
        Message(user=self.users[1], text='Am here').save()
        sqlite_sleep(.5)
        self.verify_minichat_groups([
            ['Yes', 'Am here'],
            ['Hello You'],
        ])
        self.verify_minichat_read(['Hello You'], ['Yes', 'Am here'])
        self.selenium.refresh()
        self.verify_minichat_groups([
            ['Yes', 'Am here'],
            ['Hello You'],
        ])
        self.verify_minichat_read(['Hello You', 'Yes', 'Am here'], [])
        Message(user=self.users[0], text='It is original').save()
        sqlite_sleep(.5)
        self.verify_minichat_groups([
            ['It is original'],
            ['Yes', 'Am here'],
            ['Hello You'],
        ])
        self.verify_minichat_read(['Hello You', 'Yes', 'Am here', 'It is original'], [])
        Message(user=self.users[1], text='Yup.').save()
        sqlite_sleep(.5)
        self.verify_minichat_groups([
            ['Yup.'],
            ['It is original'],
            ['Yes', 'Am here'],
            ['Hello You'],
        ])
        self.verify_minichat_read(['Hello You', 'Yes', 'Am here', 'It is original'], ['Yup.'])
        Message(user=self.users[0], text='ok...').save()
        sqlite_sleep(.5)
        self.verify_minichat_groups([
            ['ok...'],
            ['Yup.'],
            ['It is original'],
            ['Yes', 'Am here'],
            ['Hello You'],
        ])
        self.verify_minichat_read(['Hello You', 'Yes', 'Am here', 'It is original', 'Yup.',
                                   'ok...'], [])
        Message(user=self.users[1], text='what ok?').save()
        sqlite_sleep(.5)
        self.verify_minichat_groups([
            ['what ok?'],
            ['ok...'],
            ['Yup.'],
            ['It is original'],
            ['Yes', 'Am here'],
            ['Hello You'],
        ])
        self.verify_minichat_read(['Hello You', 'Yes', 'Am here', 'It is original', 'Yup.',
                                   'ok...'], ['what ok?'])
        Message(user=self.users[0], text='does not matter').save()
        sqlite_sleep(.5)
        self.verify_minichat_groups([
            ['does not matter'],
            ['what ok?'],
            ['ok...'],
            ['Yup.'],
            ['It is original'],
            ['Yes', 'Am here'],
            ['Hello You'],
        ])
        self.verify_minichat_read(['Hello You', 'Yes', 'Am here', 'It is original', 'Yup.',
                                   'ok...', 'what ok?', 'does not matter'], [])
        Message(user=self.users[0], text='brb').save()
        sqlite_sleep(.5)
        self.verify_minichat_groups([
            ['does not matter', 'brb'],
            ['what ok?'],
            ['ok...'],
            ['Yup.'],
            ['It is original'],
            ['Yes', 'Am here'],
            ['Hello You'],
        ])
        self.verify_minichat_read(['Hello You', 'Yes', 'Am here', 'It is original', 'Yup.',
                                   'ok...', 'what ok?', 'does not matter', 'brb'], [])
        Message(user=self.users[0], text='ZZz').save()
        self.verify_minichat_groups([
            ['does not matter', 'brb', 'ZZz'],
            ['what ok?'],
            ['ok...'],
            ['Yup.'],
            ['It is original'],
            ['Yes', 'Am here'],
            ['Hello You'],
        ])
        self.verify_minichat_read(['Hello You', 'Yes', 'Am here', 'It is original', 'Yup.',
                                   'ok...', 'what ok?', 'does not matter', 'brb', 'ZZz'], [])

    @logged_in_test()
    def test_not_same_day(self):
        Message(user=self.users[0], text='All my troubles..').save()
        sqlite_sleep(.5)
        message = Message.objects.latest()
        message.date = message.date - timedelta(1)
        message.save()
        sqlite_sleep(.5)
        Message(user=self.users[0], text='Hello World!').save()
        groups = [
            [ 'Hello World!', ],
            [ 'All my troubles..' ],
        ]
        self.verify_minichat_groups(groups)

    def test_message_before_login(self):
        self.login('user1', 'user1', False)
        self.logout()
        Message(user=self.users[2], text='No one is there').save()
        self.login('user1', 'user1', False)
        self.verify_minichat_groups([
            [ 'No one is there', ],
        ])
        self.verify_minichat_read([], [ 'No one is there', ])
