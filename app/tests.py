import time
from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from blog.models import BlogPost
from board.models import Thread
from minichat.models import Message
from notifications.models import Notification
from slogan.models import Slogan

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from tests_helpers import LexpageTestCase, login_required, GhostDriverBug358

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


class ViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def test_homepage(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_no_blogpost(self):
        # Remove existing blog posts
        BlogPost.objects.all().delete()

        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['post_list']), 0)

    def test_no_thread(self):
        # Remove existing threads
        Thread.objects.all().delete()

        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['thread_list']), 0)

    def test_recent_thread(self):
        # Remove existing threads
        Thread.objects.all().delete()
        thread = Thread(title='Test thread', slug='test-thread')
        thread.save()
        message = thread.post_message(User.objects.get(username='user1'), 'foo')
        message.save()

        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['thread_list']), 1)

class WebsocketsTests(LexpageTestCase):
    """ Those tests use a Firefox browser to test the websockets."""
    fixtures = ['devel']

    @classmethod
    def setUpClass(cls):
        cls.second_selenium = cls.newWebDriver()
        super(WebsocketsTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.second_selenium.quit()
        super(WebsocketsTests, cls).tearDownClass()


    @login_required()
    def testSameUserMessageMinichat(self):
        text_message = 'Je suis un test'
        text_message_xpath = '//div[@class="minichat-text" and text()[contains(.,"%s")]]' % text_message
        self.wait_for_minichat_ready()
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(text_message_xpath)
        text_input = self.selenium.find_element_by_name("text")
        text_input.send_keys(text_message)
        text_input.send_keys(Keys.RETURN)
        WebDriverWait(self.selenium, 1).until(
            lambda driver: driver.find_element_by_xpath(text_message_xpath))

    @login_required()
    def testSameUserCorrectMessageMinichat(self):
        """Test that a user can send a message, that it is displayed, then that the user
        can correct the message and that the old one is removed."""
        text_message = 'Je suis un bon test'
        text_message_xpath = '//div[@class="minichat-text" and text()[contains(.,"%s")]]' % text_message
        fix_text_message = 's/bon/mauvais'
        fixed_text_message = 'Je suis un mauvais test'
        fixed_text_message_xpath = '//div[@class="minichat-text" and text()[contains(.,"%s")]]' % fixed_text_message
        self.wait_for_minichat_ready()
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(text_message_xpath)
        text_input = self.selenium.find_element_by_name("text")
        text_input.send_keys(text_message)
        text_input.send_keys(Keys.RETURN)
        WebDriverWait(self.selenium, 1).until(
            lambda driver: driver.find_element_by_xpath(text_message_xpath))
        text_input.send_keys(fix_text_message)
        text_input.send_keys(Keys.RETURN)
        WebDriverWait(self.selenium, 1).until(
            lambda driver: driver.find_element_by_xpath(fixed_text_message_xpath))
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(text_message_xpath)

    @login_required()
    def testExternalUserMessageMinichat(self):
        """Test that another user can send a message, and that it gets displayed."""
        text_message = 'ATTENTION JE SUIS ADMIN HEIN'
        text_message_xpath = '//div[@class="minichat-text" and text()[contains(.,"%s")]]' % text_message
        self.wait_for_minichat_ready()
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(text_message_xpath)
        Message(user=User.objects.get(username='admin'), text=text_message).save()
        WebDriverWait(self.selenium, 1).until(
            lambda driver: driver.find_element_by_xpath(text_message_xpath))

    @login_required()
    def testSameUserNotificationCount(self):
        """In this test we send a notification that hilights the current user. We then test that the
        number of notifications is updated in the page."""
        text_message = '@user1 Test'
        text_message_xpath = '//div[@class="minichat-text" and text()[contains(.,"%s")]]' % text_message
        self.wait_for_minichat_ready()
        self.check_notification_count(1)
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(text_message_xpath)
        text_input = self.selenium.find_element_by_name("text")
        text_input.send_keys(text_message)
        text_input.send_keys(Keys.RETURN)
        WebDriverWait(self.selenium, 3).until(
            lambda driver: driver.find_element_by_xpath(text_message_xpath))
        self.check_notification_count(2)


    @login_required()
    @login_required('admin', 'admin', webdriver='second_selenium')
    def testConversationNotificationCount(self):
        """Take two users and make them discuss in the minichat."""
        messages = [
            {'text': '@admin Bonjour',
             'user': 'user1',
             'notifications': {'user1': 1, 'admin': 1}},
            {'text': '@user1 Hello',
             'user': 'user1',
             'notifications': {'user1': 2, 'admin': 1}},
            {'text': 'R U fine',
             'user': 'user1',
             'notifications': {'user1': 2, 'admin': 1}},
            {'text': 'yes',
             'user': 'admin',
             'notifications': {'user1': 2, 'admin': 1}},
            {'text': 'what about you',
             'user': 'admin',
             'notifications': {'user1': 2, 'admin': 1}},
            {'text': '@admin yes, thx',
             'user': 'user1',
             'notifications': {'user1': 2, 'admin': 2}},
        ]
        webdrivers = {'user1': 'selenium', 'admin': 'second_selenium'}
        for message in messages:
            user = message['user']
            wd_name = webdrivers[user]
            text_message = message['text']
            text_message_xpath = '//div[@class="minichat-text" and text()[contains(.,"%s")]]' % text_message
            for i in webdrivers.values():
                self.wait_for_minichat_ready(webdriver=i)
                wd = self.get_webdriver(i)
                with self.assertRaises(NoSuchElementException):
                    wd.find_element_by_xpath(text_message_xpath)
            user_wd = self.get_webdriver(wd_name)
            text_input = user_wd.find_element_by_name("text")
            text_input.send_keys(text_message)
            text_input.send_keys(Keys.RETURN)
            for i in webdrivers.values():
                wd = self.get_webdriver(i)
                WebDriverWait(wd, 3).until(
                    lambda driver: driver.find_element_by_xpath(text_message_xpath))
            for user, notifications in message['notifications'].items():
                self.check_notification_count(notifications, webdriver=webdrivers[user])

    @GhostDriverBug358
    @login_required()
    def testDismissNotifications(self):
        self.wait_for_minichat_ready()
        self.check_notification_count(1)
        for i in range(2, 11):
            notification = {
                'title': 'Foobar',
                'description': 'this is a test',
                'recipient': User.objects.get(username='user1'),
                'app': 'game',
                'key': 'bar',
            }
            Notification(**notification).save()
            time.sleep(1)
            self.check_notification_count(i)
        notif_xpath = '//span[@class="fa fa-bell" and text()=" 10"]'
        notification_icon = self.selenium.find_element_by_xpath(notif_xpath)
        ActionChains(self.selenium).move_to_element(notification_icon).perform()
        dismiss_xpath = '(//div[@class="notification_dismiss"])[1]'
        for i in range(0, 10):
            time.sleep(0.5)
            dismiss_link = self.selenium.find_element_by_xpath(dismiss_xpath)
            dismiss_link.click()
        time.sleep(5)
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(dismiss_xpath)

class LoginTests(LexpageTestCase):
    """Simple login tests"""
    fixtures = ['devel']

    def testLoginAsRegularUser(self):
        """Test login as a regular user"""
        self.login('user1', 'user1')

    def testLoginAsRegularUserIsCaseInsensitive(self):
        """Test login as a regular user with a capitalized login"""
        self.login('user1', 'user1')

    def testLoginAsRegularUserWithWrongPassword(self):
        """Test login as a regular user but with a wrong password"""
        self.login_failure('user1', 'User1')

    def testLoginAsAdminUser(self):
        """Test login as an admin user"""
        self.login('admin', 'admin')

    def testLoginAsAdminUserIsCaseInsensitive(self):
        """Test login as an admin user with a capitalized login"""
        self.login('ADMIN', 'admin', 'admin')

    def testLoginAsAdminUserCaseInsensitiveWithWrongPassword(self):
        """Test login as an admin user with a capitalized username but with a wrong password"""
        self.fill_in_login_form('Admin', 'Admin')

    def testLoginAsNonExistingUser(self):
        """Test login as a non-existing users"""
        self.login_failure('bob', 'champignon')


class HomepageTests(LexpageTestCase):
    """Browser tests for the homepage"""
    fixtures = ['devel']

    def setUp(self):
        super(LexpageTestCase, self).setUp()
        self.selenium.get('%s' % (self.live_server_url))

    def testNoThreadsAreDisplayedOnTheHomepage(self):
        """On the homepage there are no open discussions that should be displayed by default with
        the devel fixtures."""
        emtext = self.selenium.find_element_by_css_selector('.pagecontent > em')
        self.assertEqual(emtext.text, 'Aucun discussion récente.')

    def testSloganInSlogans(self):
        all_text = []
        for slogan in Slogan.visible.all():
            all_text.append(slogan.slogan)
        current_text = self.selenium.find_element_by_css_selector('#slogan > em').text
        self.assertIn('   %s   ' % current_text, all_text)

    def testYearInFooter(self):
        footer_text = self.selenium.find_element_by_css_selector('.footer > .container > p').text
        self.assertIn('1996-%s' % date.today().year, footer_text)

    def testNewThread(self):
        Thread.objects.all().delete()
        thread = Thread(title='Test thread', slug='test-thread')
        thread.save()
        message = thread.post_message(User.objects.get(username='user1'), 'foo')
        message.save()
        self.selenium.refresh()
        self.assertIsNotNone(self.selenium.find_element_by_link_text('Test thread'))

