import datetime
import time

from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturalday
from django.core.cache import cache
from django.urls import reverse
from helpers.selenium import *
from minichat.models import Message
from minichat.templatetags.minichat import highlight_anchor
from selenium.webdriver.common.keys import Keys


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


class MinichatSeleniumTests(LexpageSeleniumTestCase):
    def force_minichat_refresh(self):
        self.wait_for_minichat()
        self.selenium.execute_script('app_minichat.reset();')
        self.selenium.execute_script('app_minichat.refresh();')
        WebDriverWait(self.selenium, self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.minichat-group'))
        )

    def wait_for_minichat(self):
        WebDriverWait(self.selenium, self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.minichat-content'))
        )


class RemainingChars(MinichatSeleniumTests):
    fixtures = ['devel']

    def setUp(self):
        super().setUp()
        self.login()
        self.wait_for_minichat()

        self.input_element = self.selenium.find_element_by_css_selector(
            self.selenium.execute_script('return app_minichat._input_text_selector;')
        )

        self.remaining_element = self.selenium.find_element_by_css_selector(
            self.selenium.execute_script('return app_minichat._remaining_chars_selector;')
        )

        self.button_element = self.selenium.find_element_by_css_selector(
            self.selenium.execute_script('return app_minichat._button_selector;')
        )

        self.initial = self.get_remaining_chars()

    def get_remaining_chars(self):
        return int(self.remaining_element.text.split()[0])

    def test_starts_with_150(self):
        self.assertEqual(self.initial, 150)

    def test_decreases_when_typing(self):
        for i, char in enumerate('Hello! How are you? Did you known that the minichat is currently working?'):
            self.input_element.send_keys(char)
            self.assertEqual(self.get_remaining_chars(), self.initial - i - 1)

    def test_increases_when_backspacing(self):
        text = 'Hello World!'
        self.input_element.send_keys(text)
        self.assertEqual(self.get_remaining_chars(), self.initial - len(text))

        for i in range(len(text)):
            self.input_element.send_keys(Keys.BACK_SPACE)
            self.assertEqual(self.get_remaining_chars(), self.initial - len(text) + i + 1)

    def test_cannot_go_below_0(self):
        while self.get_remaining_chars() > 0:
            self.input_element.send_keys('Hello World!')

        self.assertEqual(self.get_remaining_chars(), 0)
        self.input_element.send_keys('Hello World!')

        self.assertEqual(self.get_remaining_chars(), 0)
        self.input_element.send_keys(Keys.CONTROL + 'a')
        self.input_element.send_keys(Keys.DELETE)

        self.assertEqual(self.get_remaining_chars(), self.initial)

    def test_reset_after_post(self):
        self.input_element.send_keys('Hello world! This is a test!')

        # Reset to dismiss existing .minichat-text-content
        self.selenium.execute_script('app_minichat.reset();')

        self.button_element.click()
        WebDriverWait(self.selenium, self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.minichat-text-content'))
        )
        message = self.selenium.find_element_by_css_selector('.minichat-text-content')
        self.assertIn('Hello world! This is a test!', message.text)

    def test_post_empty_message(self):
        """
        Empty message should display a proper error message.
        See https://github.com/AlexandreDecan/Lexpage/issues/176
        """
        self.button_element.click()

        message = self.selenium.find_element_by_css_selector('.contrib-messages .alert-danger')
        self.assertNotIn('{"text":["Ce champ ne peut être vide."]}', message.text)
        self.assertIn('Ce champ ne peut être vide.', message.text)


class MessageVisibilityTests(MinichatSeleniumTests):
    fixtures = ['devel']

    def setUp(self):
        super().setUp()
        self.author = User.objects.all()[0]
        Message.objects.all().delete()
        self.go()

    def post_message(self, text_message='Hello World', timeout=0):
        """
        Ensure that given message is visible after given delay.
        """
        # Ensure message was not already visible
        text_element = '//*[@class="minichat-text-content" and contains(.,"%s")]' % text_message
        with self.assertRaises(exceptions.NoSuchElementException):
            self.selenium.find_element_by_xpath(text_element)

        # Create new message
        Message.objects.create(user=self.author, text=text_message)

        # If bool(timeout) is False, then force refresh
        if not bool(timeout):
            self.force_minichat_refresh()
        else:
            WebDriverWait(self.selenium, timeout).until(
                lambda driver: driver.find_element_by_xpath(text_element))

    def test_post_message(self):
        """
        A message should be visible if posted and minichat is refreshed.
        """
        self.wait_for_minichat()
        self.post_message('Message 1')

    def test_post_message_delay(self):
        """
        A message should be visible after maximum x seconds when posted.
        :return:
        """
        self.login()
        self.wait_for_minichat()

        timeout = self.selenium.execute_script('return app_minichat.timer_delay;')
        self.post_message('Message 2', timeout=timeout + self.timeout)

    def test_post_message_delay_logged_out(self):
        """
        Message delay is longer for logged out users.
        """
        self.login()
        timeout = self.selenium.execute_script('return app_minichat.timer_delay;')
        self.logout()
        self.wait_for_minichat()

        with self.assertRaises(exceptions.TimeoutException):
            self.post_message('Message 3', timeout=timeout + self.timeout)


class MessagesGroupingTests(MinichatSeleniumTests):
    def setUp(self):
        super().setUp()

        # Running the tests just before midnight could cause failures
        if time.strftime("%H%M") in ['2358', '2359']:  # pragma: no cover
            self.sleep(125)

        self.users = [
            User.objects.create_user(username=username, email='%s@example.com' % username, password=username)
            for username in ('user1', 'user2', 'user3')
        ]

        self.go()
        self.wait_for_minichat()

    def check_groups(self, groups):
        """
        Check that messages are split correctly into groups.
        *groups* is a list of list of message text. Messages should be given in chronological order!
        """
        self.force_minichat_refresh()

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
        Message.objects.create(user=self.users[0], text='m1')
        Message.objects.create(user=self.users[1], text='m2')
        Message.objects.create(user=self.users[0], text='m3')
        Message.objects.create(user=self.users[1], text='m4')
        Message.objects.create(user=self.users[0], text='m5')

        self.check_groups([['m1'], ['m2'], ['m3'], ['m4'], ['m5']])

    def test_group_messages_by_author(self):
        """
        Messages having the same author should be grouped if they are posted consecutively in a short period of time.
        """
        Message.objects.all().delete()
        Message.objects.create(user=self.users[0], text='m1')
        Message.objects.create(user=self.users[0], text='m2')
        Message.objects.create(user=self.users[0], text='m3')

        Message.objects.create(user=self.users[1], text='m4')
        Message.objects.create(user=self.users[1], text='m5')
        Message.objects.create(user=self.users[1], text='m6')

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


class MessagesHighlightingTests(MinichatSeleniumTests):
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
        super().setUp()

        self.users = [
            User.objects.create_user(username=username, email='%s@example.com' % username, password=username)
            for username in ('user1', 'user2', 'user3')
        ]

        # Wait for app_minichat to be loaded
        self.go()
        self.wait_for_minichat()

    def post_message(self, message):
        Message.objects.all().delete()
        Message.objects.create(user=self.users[0], text=message)
        self.force_minichat_refresh()

    def test_no_highlight_for_visitors(self):
        """
        Visitors should never see a bold anchor.
        """
        for message, nb in MessagesHighlightingTests.test_cases:
            self.post_message(message)
            highlights = self.selenium.find_elements_by_css_selector('.minichat-text-content .highlight')
            self.assertEqual(len(highlights), 0, 'Failed with {}'.format(message))

    def test_no_highlight_for_user3(self):
        """
        User3 should never see a bold anchor, as it is not the target of registered anchors.
        """
        self.login('user3', 'user3')
        for message, nb in MessagesHighlightingTests.test_cases:
            self.post_message(message)
            highlights = self.selenium.find_elements_by_css_selector('.minichat-text-content .highlight')
            self.assertEqual(len(highlights), 0, 'Failed with {}'.format(message))

    def test_highlight_for_user1(self):
        """
        User1 should see bold anchors, as it is the target of some of them (see *test_cases*).
        """
        self.login('user1', 'user1')
        for message, nb in MessagesHighlightingTests.test_cases:
            self.post_message(message)

            highlights = self.selenium.find_elements_by_css_selector('.minichat-text-content .highlight')
            self.assertEqual(len(highlights), nb, 'Failed with {}'.format(message))

    def test_feature_parity(self):
        for message, nb in MessagesHighlightingTests.test_cases:
            js_result = self.selenium.execute_script('return env.getFilter("highlightAnchor")("{}", "{}");'.format(message, 'user1'))
            django_result = highlight_anchor(message, 'user1')
            # Feature parity
            self.assertEqual(js_result, django_result)


class ReadingStatusTests(MinichatSeleniumTests):
    def setUp(self):
        super().setUp()

        self.users = [
            User.objects.create_user(username=username, email='%s@example.com' % username, password=username)
            for username in ('user1', 'user2', 'user3')
        ]

        Message.objects.all().delete()
        self.go()

    def check_read_and_unread_messages(self, m_read, m_unread):
        """
        Check that messages are either read or unread according to given lists of expected read/unread
        message contents.
        """
        self.force_minichat_refresh()

        expected_read = set(m_read)
        expected_unread = set(m_unread)

        all_messages = self.selenium.find_elements_by_css_selector('.minichat-text')
        unread_messages = self.selenium.find_elements_by_css_selector('.minichat-text.new')

        read = set()
        unread = set()
        for message in unread_messages:
            text = message.find_element_by_css_selector('.minichat-text-content').text
            unread.add(text)
        for message in all_messages:
            text = message.find_element_by_css_selector('.minichat-text-content').text
            if text not in unread:
                read.add(text)

        self.assertSetEqual(expected_read, read)
        self.assertSetEqual(expected_unread, unread)

    def test_messages_are_read(self):
        Message.objects.create(user=self.users[0], text='m1')
        Message.objects.create(user=self.users[1], text='m2')
        Message.objects.create(user=self.users[1], text='m3')
        Message.objects.create(user=self.users[2], text='m4')
        Message.objects.create(user=self.users[2], text='m5')

        self.login()  # Login after to have last_visit = now()

        self.check_read_and_unread_messages(['m1', 'm2', 'm3', 'm4', 'm5'], [])

    def test_new_messages_are_unread(self):
        self.login()  # Login before to have last_visit < message.date

        Message.objects.create(user=self.users[1], text='m1')
        Message.objects.create(user=self.users[1], text='m2')
        Message.objects.create(user=self.users[1], text='m3')

        self.check_read_and_unread_messages([], ['m1', 'm2', 'm3'])

    def test_messages_by_self_are_read(self):
        self.login()  # Login before to have last_visit < message.date

        Message.objects.create(user=self.users[1], text='m1')
        Message.objects.create(user=self.users[0], text='m2')
        Message.objects.create(user=self.users[0], text='m3')
        Message.objects.create(user=self.users[1], text='m4')

        self.check_read_and_unread_messages(['m2', 'm3'], ['m1', 'm4'])

    def test_mixed_read_and_unread(self):
        Message.objects.create(user=self.users[1], text='m1')
        Message.objects.create(user=self.users[1], text='m2')
        Message.objects.create(user=self.users[2], text='m3')

        self.login()  # Login between the two groups

        Message.objects.create(user=self.users[1], text='m4')
        Message.objects.create(user=self.users[1], text='m5')
        Message.objects.create(user=self.users[2], text='m6')

        self.check_read_and_unread_messages(['m1', 'm2', 'm3'], ['m4', 'm5', 'm6'])

    def test_read_unread_for_visitors(self):
        Message.objects.create(user=self.users[0], text='m1')
        Message.objects.create(user=self.users[1], text='m2')

        self.go()

        Message.objects.create(user=self.users[1], text='m3')
        Message.objects.create(user=self.users[2], text='m4')

        self.check_read_and_unread_messages(['m1', 'm2'], ['m3', 'm4'])
