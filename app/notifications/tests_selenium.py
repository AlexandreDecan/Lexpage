from django.contrib.auth.models import User
from django.core.cache import cache
from helpers.selenium import *

from notifications.models import Notification
from selenium.webdriver.common.action_chains import ActionChains


class NotificationsSeleniumTests(LexpageSeleniumTestCase):
    def setUp(self):
        # Reset cache
        cache.clear()

    def force_notifications_refresh(self):
        self.selenium.execute_script('app_notifications.reset();')
        self.selenium.execute_script('app_notifications.refresh();')

        WebDriverWait(self.selenium, self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.notification_list .notification'))
        )
        element = self.selenium.find_element_by_css_selector('#notifications_container .dropdown-toggle')
        other_element = self.selenium.find_element_by_css_selector('h2')
        ActionChains(self.selenium).move_to_element(other_element).move_to_element(element).perform()


class NotificationsDisplayTests(NotificationsSeleniumTests):
    def setUp(self):
        super().setUp()

        self.users = [
            User.objects.create_user(username=username, email='%s@example.com' % username, password=username)
            for username in ('user1', 'user2', 'user3')
        ]

        Notification.objects.all().delete()

        # Create a notification for user2 and user3, this should have NO effect for user1
        Notification.objects.get_or_create(recipient=self.users[1], app='test', key='1', title='hello', description='hellodesc')
        Notification.objects.get_or_create(recipient=self.users[2], app='test', key='1', title='world', description='worlddesc')

    def test_no_notification(self):
        self.login()
        with self.assertRaises(exceptions.TimeoutException):
            self.force_notifications_refresh()

    def test_notification_displayed(self):
        """
        An existing notification should be displayed.
        """
        # Create a notification that should be displayed
        Notification.objects.get_or_create(recipient=self.users[0], app='test', key='1', title='salut', description='coucou')

        self.login()
        WebDriverWait(self.selenium, self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.notification_list .notification'))
        )
        self.selenium.find_element_by_css_selector('#notifications_container .dropdown-toggle').click()

        notifications = self.selenium.find_elements_by_css_selector('.notification_title')
        self.assertEqual(len(notifications), 1)
        self.assertEqual(notifications[-1].text, 'salut')

    def test_new_notification(self):
        """
        If a notification is already displayed, trigger a new one and it should be displayed too.
        """
        self.test_notification_displayed()  # Create a notification

        # Add a new one and refresh
        Notification.objects.get_or_create(recipient=self.users[0], app='test', key='2', title='salut1', description='coucou1')
        self.force_notifications_refresh()

        notifications = self.selenium.find_elements_by_css_selector('.notification_title')
        self.assertEqual(len(notifications), 2)
        self.assertEqual(notifications[-1].text, 'salut1')

    def test_notifications_timeout(self):
        """
        Notifications list should be refreshed after a given amount of time
        """
        # Create a notification such that the list appears on page load
        notif, _ = Notification.objects.get_or_create(recipient=self.users[0], app='test', key='1', title='salut1', description='coucou1')

        self.login()
        # Force refresh such that the notification list appears
        self.force_notifications_refresh()

        # Remove the notification and wait for refresh
        notif.delete()
        timeout = self.selenium.execute_script('return app_notifications.timer_delay;')
        WebDriverWait(self.selenium, timeout + self.timeout).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.notification_list'), 'salut1')
        )


class NotificationsDismissTests(NotificationsSeleniumTests):
    def setUp(self):
        super().setUp()
        user = User.objects.create_user(username='user1', email='user1@example.com', password='user1')

        # Create several notifications
        Notification.objects.all().delete()
        Notification.objects.get_or_create(recipient=user, app='test', key='1', title='salut1', description='coucou1')
        Notification.objects.get_or_create(recipient=user, app='test', key='2', title='salut2', description='coucou2')
        Notification.objects.get_or_create(recipient=user, app='test', key='3', title='salut3', description='coucou3')

        self.login()
        self.force_notifications_refresh()

    def test_dismiss_one_notification(self):
        """
        Notifications list shouldn't list dismissed notifications.
        """
        self.assertEqual(len(self.selenium.find_elements_by_css_selector('.notification_list .notification')), 3)

        # Dismiss one of them
        self.selenium.find_element_by_css_selector('.notification_list .notification .close').click()
        self.force_notifications_refresh()

        self.assertEqual(len(self.selenium.find_elements_by_css_selector('.notification_list .notification')), 2)

    def test_dismiss_all_notifications(self):
        """
        Notifications list should disappear if we dismiss all notifications.
        """
        self.assertEqual(len(self.selenium.find_elements_by_css_selector('.notification_list .notification')), 3)

        # Dismiss all of them
        element = self.selenium.find_element_by_css_selector('.notification_list .close')
        element.click()
        WebDriverWait(self.selenium, self.timeout).until(
            EC.staleness_of(element)
        )

        element = self.selenium.find_element_by_css_selector('.notification_list .close')
        element.click()
        WebDriverWait(self.selenium, self.timeout).until(
            EC.staleness_of(element)
        )

        self.selenium.find_element_by_css_selector('.notification_list .close').click()
        WebDriverWait(self.selenium, self.timeout).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.notification_list .notification'))
        )



