import datetime
import time

from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturalday
from django.core.urlresolvers import reverse
from helpers.selenium import *
from selenium.common.exceptions import NoSuchElementException
from .models import Message


class NaturalDayFilterTests(LexpageSeleniumTestCase):
    def test_invalid_date(self):
        """
        An invalid date should provoke an "Invalid date" message.
        :return:
        """
        self.go()
        filter_invalid_date = self.selenium.execute_script('return env.getFilter("naturalDay")("foo");');
        self.assertEqual(filter_invalid_date, 'Invalid date')

    def test_feature_parity(self):
        """
        Ensure that Nunjuck's naturalDay filter has a feature parity with Django's one.
        """
        urls = [
            '',
            # See https://github.com/AlexandreDecan/Lexpage/issues/155
            reverse('search')
        ]

        for url in urls:
            with self.subTest(url=url):
                self.go(url)
                # One year and 30 days
                for i in range(0, 365+30):
                    d = datetime.date.today() - datetime.timedelta(days=i)
                    filter_date = self.selenium.execute_script('return env.getFilter("naturalDay")("%s");' % d.isoformat())
                    self.assertEqual(filter_date, naturalday(d, 'l j b.'))


class MessageVisibilityTests(LexpageSeleniumTestCase):
    fixtures = ['devel']

    def setUp(self):
        self.go()
        WebDriverWait(self.selenium, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.minichat-content'))
        )

        self.users = User.objects.all()
        self.author = self.users[0]

    def post_message(self, text_message='Hello World', timeout=0):
        """
        Ensure that given message is visible after given delay.
        """

        # Ensure message was not already visible
        text_message_xpath = '//div[@class="minichat-text" and contains(.,"%s")]' % text_message
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(text_message_xpath)

        # Create new message
        Message(user=self.author, text=text_message).save()

        # If bool(timeout) is False, then force refresh
        if not bool(timeout):
            self.selenium.execute_script('app_minichat.refresh_content();')
            timeout = 0

        # Message should be visible
        WebDriverWait(self.selenium, timeout + 1).until(
            lambda driver: driver.find_element_by_xpath(text_message_xpath))

    def test_post_message(self):
        """
        A message should be visible if posted and minichat is refreshed.
        """
        self.post_message('Message 1')

    def test_post_message_delay(self):
        """
        A message should be visible after maximum 10 seconds when posted.
        :return:
        """
        self.post_message('Message 2', timeout=10)


class MessagesGroupingTests(LexpageSeleniumTestCase):
    def setUp(self):
        # Running the tests just before midnight could cause failures
        if time.strftime("%H%M") in ['2358', '2359']:  # pragma: no cover
            self.sleep(125)

        self.users = [
            User.objects.create_user(username=username, email='%s@example.com' % username, password=username)
            for username in ('user1', 'user2', 'user3')
        ]
        for user in self.users:
            user.save()

        # Wait for app_minichat to be loaded
        self.go()
        WebDriverWait(self.selenium, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.minichat-content'))
        )

    def check_groups(self, groups):
        """
        Check that messages are split correctly into groups.
        *groups* is a list of list of message text. Messages should be given in chronological order!
        """
        self.selenium.execute_script('app_minichat.refresh_content();')
        self.selenium.implicitly_wait(1)

        displayed_groups = self.selenium.find_elements_by_css_selector('.minichat-group')

        self.assertEqual(len(groups), len(displayed_groups))
        for i, group in enumerate(groups[::-1]):
            displayed_messages = displayed_groups[i].find_elements_by_css_selector('.minichat-text-content')
            self.assertEqual(len(group), len(displayed_messages))
            for j, message in enumerate(group):
                self.assertEqual(message, displayed_messages[j].text)

    def test_alternating_messages(self):
        """
        Alternating authors should not be grouped.
        """
        Message.objects.all().delete()
        Message(user=self.users[0], text='m1').save()
        Message(user=self.users[1], text='m2').save()
        Message(user=self.users[0], text='m3').save()
        Message(user=self.users[1], text='m4').save()
        Message(user=self.users[0], text='m5').save()

        self.check_groups([['m1'], ['m2'], ['m3'], ['m4'], ['m5']])

    def test_group_messages_by_author(self):
        """
        Messages having the same author should be grouped if they are posted consecutively in a short period of time.
        """
        Message.objects.all().delete()
        Message(user=self.users[0], text='m1').save()
        Message(user=self.users[0], text='m2').save()
        Message(user=self.users[0], text='m3').save()

        Message(user=self.users[1], text='m4').save()
        Message(user=self.users[1], text='m5').save()
        Message(user=self.users[1], text='m6').save()

        self.check_groups([['m1', 'm2', 'm3'], ['m4', 'm5','m6']])

    def test_split_group_after_delay(self):
        """
        Messages from a similar author should be split if they are posted after a while.
        """
        Message.objects.all().delete()
        messages = [
            Message(user=self.users[0], text='m1'),
            Message(user=self.users[0], text='m2'),
            Message(user=self.users[0], text='m3'),
            Message(user=self.users[0], text='m4'),
            Message(user=self.users[0], text='m5')
        ]

        for i, message in enumerate(messages):
            message.save()
            # Delay m3 and m5
            if i >= 2:
                message.date += datetime.timedelta(minutes=8)
            if i >= 4:
                message.date += datetime.timedelta(minutes=8)
            message.save()

        self.check_groups([['m1', 'm2'], ['m3', 'm4'], ['m5']])


class MessagesHighlightingTests(LexpageSeleniumTestCase):
    test_cases = [
        ('coucou @user1', 1),
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
        ('@user2', 0)
    ]

    def setUp(self):
        self.users = [
            User.objects.create_user(username=username, email='%s@example.com' % username, password=username)
            for username in ('user1', 'user2', 'user3')
        ]
        for user in self.users:
            user.save()

        # Wait for app_minichat to be loaded
        self.go()
        WebDriverWait(self.selenium, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.minichat-content'))
        )

    def post_message(self, message):
        Message.objects.all().delete()
        Message(user=self.users[0], text=message).save()

        self.selenium.execute_script('app_minichat.refresh_content();')
        WebDriverWait(self.selenium, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.minichat-text-content'))
        )

    def test_no_highlight_for_visitors(self):
        """
        Visitors should never see a bold anchor.
        """
        for message, nb in MessagesHighlightingTests.test_cases:
            self.post_message(message)
            highlights = self.selenium.find_elements_by_css_selector('.minichat-text-content strong')
            self.assertEqual(len(highlights), 0, 'Failed with {}'.format(message))

    def test_no_highlight_for_user3(self):
        """
        User3 should never see a bold anchor, as it is not the target of registered anchors.
        """
        self.login('user3', 'user3')
        for message, nb in MessagesHighlightingTests.test_cases:
            self.post_message(message)
            highlights = self.selenium.find_elements_by_css_selector('.minichat-text-content strong')
            self.assertEqual(len(highlights), 0, 'Failed with {}'.format(message))

        self.logout()

    def test_highlight_for_user1(self):
        """
        User1 should see bold anchors, as it is the target of some of them (see *test_cases*).
        """
        self.login('user1', 'user1')
        for message, nb in MessagesHighlightingTests.test_cases:
            self.post_message(message)
            highlights = self.selenium.find_elements(By.CSS_SELECTOR, '.minichat-text-content strong')
            self.assertEqual(len(highlights), nb, 'Failed with {}'.format(message))

        self.logout()

#TODO: Test read/unread?
#TODO: Tests for notification (can be seen, updated, can be removed)