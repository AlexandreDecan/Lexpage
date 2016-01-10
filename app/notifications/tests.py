import time

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from notifications.models import Notification
from tests_helpers import LexpageTestCase, logged_in_test, SELENIUM_AVAILABLE

if SELENIUM_AVAILABLE:
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import NoSuchElementException
    from selenium.webdriver.support import expected_conditions as EC

class NotificationTests(TestCase):
    fixtures = ['devel']

    def test_dismiss_notification_logged_out(self):
        """A logged out user can not dismiss a notification"""
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 1)
        response = self.client.delete(reverse('notification_api_dismiss', kwargs={'pk': notifications[0].id}))
        self.assertEqual(response.status_code, 403)
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 1)

    def test_dismiss_notification_logged_in(self):
        self.client.login(username='user1', password='user1')
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 1)
        notification_id = notifications[0].id
        response = self.client.delete(reverse('notification_api_dismiss', kwargs={'pk': notification_id}))
        self.assertEqual(response.status_code, 204)
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 0)
        response = self.client.delete(reverse('notification_api_dismiss', kwargs={'pk': notification_id}))
        self.assertEqual(response.status_code, 404)

    def test_dismiss_notification_other_user(self):
        User.objects.create_user(
            username='user2', email='user2@example.com', password='top_secret')
        self.client.login(username='user2', password='top_secret')
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 1)
        response = self.client.delete(reverse('notification_api_dismiss', kwargs={'pk': notifications[0].id}))
        self.assertEqual(response.status_code, 404)
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 1)

    def test_dismiss_notification_by_showing(self):
        self.client.login(username='user1', password='user1')
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 1)
        notification_id = notifications[0].id
        response = self.client.get(reverse('notification_show', kwargs={'pk': notification_id}))
        self.assertEqual(response.status_code, 302)
        notifications = Notification.objects.filter(recipient=User.objects.get(username='user1'))
        self.assertEqual(len(notifications), 0)

    def test_list_notification_logged_out(self):
        """A logged out user can not list notifications"""
        response = self.client.get(reverse('notifications_api_list'), format='json')
        self.assertEqual(response.status_code, 403)

    def test_list_notification_logged_in(self):
        """A logged in user can list notifications"""
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('notifications_api_list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        notification = response.data[0]
        self.assertEqual(notification['description'], 'admin a entamé une nouvelle conversation avec vous : <em>Test de conversation</em>.')
        self.assertTrue(notification['dismiss_url'].endswith('/notifications/api/notification/1'))
        self.assertTrue(notification['show_and_dismiss_url'].endswith('/notifications/1'))

class NotificationBrowserTest(LexpageTestCase):
    fixtures = ['devel']

    @logged_in_test()
    def test_updated_notification_count(self):
        """
        Test that the ajax polling works to update the notifications count
        """
        self.check_notification_count(1)
        self.create_notification()
        self.check_notification_count(2, timeout=40)

    @logged_in_test()
    def test_notification_dismiss(self):
        """
        Test that when we dismiss notification they are hidden but that the dropdown stays open
        so we can dismiss several of them in a row.
        """
        self.check_notification_count(1)
        for i in range(0, 10):
            self.create_notification()
        self.selenium.refresh()
        self.check_notification_count(11)
        notif_xpath = '//a[@id="notifications_dropdown_button"]/span[@class="badge"]/span[@class="fa fa-bell"]'
        notification_icon = self.selenium.find_element_by_xpath(notif_xpath)
        ActionChains(self.selenium).move_to_element(notification_icon).perform()
        dismiss_xpath = '(//div[@class="notification_dismiss"])[1]'
        WebDriverWait(self.selenium, 1).until(
            EC.visibility_of(self.selenium.find_element_by_xpath(dismiss_xpath)))
        for i in range(11, 0, -1):
            time.sleep(0.5)
            self.check_notification_count(i)
            dismiss_link = self.selenium.find_element_by_xpath(dismiss_xpath)
            dismiss_link.click()
        time.sleep(0.5)
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(dismiss_xpath)

    def create_notification(self, user='user1'):
        notification = {
            'title': 'Foobar',
            'description': 'this is a test',
            'recipient': User.objects.get(username='user1'),
            'app': 'game',
            'key': 'bar',
        }
        Notification(**notification).save()


    def check_notification_count(self, count, timeout=5):
        """timeout can be set to a different value, e.g to test ajax pulling."""
        notif_xpath = '//span[@class="badge" and contains(text(),"%s")]' % count
        WebDriverWait(self.selenium, timeout).until(
            lambda driver: driver.find_element_by_xpath(notif_xpath))

