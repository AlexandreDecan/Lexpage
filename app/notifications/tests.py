import time

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.lorem_ipsum import words
from notifications.models import Notification
from tests_helpers import LexpageTestCase, logged_in_test, SELENIUM_AVAILABLE, sqlite_sleep

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
        self.assertEqual(len(response.data['results']), 1)
        notification = response.data['results'][0]
        self.assertEqual(response.data['total_pages'], 1)
        self.assertEqual(response.data['current_page'], 1)
        self.assertEqual(notification['description'], 'admin a entamé une nouvelle conversation avec vous : <em>Test de conversation</em>.')
        self.assertTrue(notification['dismiss_url'].endswith('/notifications/api/notification/1'))
        self.assertTrue(notification['show_and_dismiss_url'].endswith('/notifications/1'))

    def test_notifications_pagination(self):
        Notification.objects.all().delete()
        for i in range(0,53):
            notification = {
                'title': words(2, False),
                'description': words(6, False),
                'recipient': User.objects.get(username='user1'),
                'app': 'game',
                'key': 'bar',
            }
            Notification(**notification).save()
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('notifications_api_list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['count'], 53)
        self.assertEqual(response.data['total_pages'], 11)
        self.assertEqual(response.data['current_page'], 1)
        response = self.client.get(reverse('notifications_api_list'), {'page': 5}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 5)
        self.assertEqual(response.data['count'], 53)
        self.assertEqual(response.data['total_pages'], 11)
        self.assertEqual(response.data['current_page'], 5)
        response = self.client.get(reverse('notifications_api_list'), {'page': 11}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)
        self.assertEqual(response.data['count'], 53)
        self.assertEqual(response.data['total_pages'], 11)
        self.assertEqual(response.data['current_page'], 11)



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
        time.sleep(2)
        self.check_notification_count(11)
        notif_xpath = '//a[@id="notifications_dropdown_button"]'
        notification_icon = self.selenium.find_element_by_xpath(notif_xpath)
        ActionChains(self.selenium).move_to_element(notification_icon).perform()
        dismiss_all_xpath = '//div[@class="notification_dismiss"]'
        dismiss_xpath = '(%s)[1]' % dismiss_all_xpath
        WebDriverWait(self.selenium, 4).until(
            EC.visibility_of(self.selenium.find_element_by_xpath(dismiss_xpath)))
        for i in range(11, 0, -1):
            time.sleep(1.5)
            # Test pagination
            self.assertEqual(min(5, i),\
                             len(self.selenium.find_elements_by_xpath(dismiss_all_xpath)))
            self.check_notification_count(i)
            self.dismiss_notification()
        time.sleep(1)
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
        sqlite_sleep(1)

    @logged_in_test()
    def test_notification_pagination(self):
        """
        Test the pagination:
        - browse between the page
        - Check that there are no more than 5 notifications per page
        - Check that you can dismiss notifications even if you start on the last page
        """
        self.check_notification_count(1)
        for i in range(0, 12):
            self.create_notification()
        # Now we have 13 notifications
        self.check_notification_count(13)
        time.sleep(1)
        pagination_path = '//div[contains(@class, "notification_pagination")]/div[@class="text-muted small" and contains(., "%s")]'
        pagination = lambda x: self.selenium.find_element_by_xpath(pagination_path % x)
        notif_xpath = '//a[@id="notifications_dropdown_button"]'
        notification_icon = self.selenium.find_element_by_xpath(notif_xpath)
        ActionChains(self.selenium).move_to_element(notification_icon).perform()
        dismiss_all_xpath = '//div[@class="notification_dismiss"]'
        dismiss_xpath = '(%s)[1]' % dismiss_all_xpath
        WebDriverWait(self.selenium, 1).until(
            EC.visibility_of(self.selenium.find_element_by_xpath(dismiss_xpath)))
        # We should be able to dismiss everything even if we start at the last page
        time.sleep(.5)
        next_link = lambda: self.selenium.find_element_by_css_selector('.notification_pagination .next_page a')
        previous_link = lambda: self.selenium.find_element_by_css_selector('.notification_pagination .previous_page a')
        next_link().click()
        WebDriverWait(self.selenium, 2).until(
            EC.visibility_of(pagination('2/3')))
        time.sleep(0.1)
        previous_link().click()
        WebDriverWait(self.selenium, 2).until(
            EC.visibility_of(pagination('1/3')))
        time.sleep(0.1)
        with self.assertRaises(NoSuchElementException):
            previous_link() # Check that previous link does not exist
        # Then to third page
        next_link().click()
        WebDriverWait(self.selenium, 2).until(
            EC.visibility_of(pagination('2/3')))
        time.sleep(0.1)
        previous_link() # Check that it exists
        next_link().click()
        WebDriverWait(self.selenium, 2).until(
            EC.visibility_of(pagination('3/3')))
        time.sleep(0.1)
        dismiss_3_xpath = '(%s)[3]' % dismiss_all_xpath
        dismiss_4_xpath = '(%s)[4]' % dismiss_all_xpath
        # There should be 3 notifications here..
        self.selenium.find_element_by_xpath(dismiss_3_xpath)
        # But not 4!
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(dismiss_4_xpath)

        # Dismiss everything (without changing page)
        for i in range(13, 0, -1):
            time.sleep(.5)
            self.check_notification_count(i)
            self.dismiss_notification()
            # Check presence/absence of links
            # We should always stay at the last page, so it should always raise the exception
            with self.assertRaises(NoSuchElementException):
                next_link() # Check that previous link does not exist
            # If there are <= 5 notifications, we should not see the links. Otherwhise, we should:
            # i-1 because we just dismissed a notification, remember?
            if i-1 <= 5:
                with self.assertRaises(NoSuchElementException):
                    previous_link() # Check that previous link does not exist
            else:
                previous_link()

        time.sleep(0.5)
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(dismiss_xpath)


    def dismiss_notification(self):
        dismiss_all_xpath = '//div[@class="notification_dismiss"]'
        dismiss_xpath = '(%s)[1]' % dismiss_all_xpath
        dismiss_link = self.selenium.find_element_by_xpath(dismiss_xpath)
        dismiss_link.click()
        WebDriverWait(self.selenium, 2).until_not(
            lambda driver: driver.find_element_by_css_selector("a.close.fa-spinner.fa-spin"))

    def check_notification_count(self, count, timeout=5):
        """timeout can be set to a different value, e.g to test ajax pulling."""
        notif_xpath = '//span[@class="badge" and contains(text(),"%s")]' % count
        WebDriverWait(self.selenium, timeout).until(
            lambda driver: driver.find_element_by_xpath(notif_xpath))

    @logged_in_test()
    def test_safe_title_function(self):
        titles = (
            ('Foobar', 'Foobar'),
            ('Foobar(1)', 'Foobar⟨1⟩'),
            ('Foobar()', 'Foobar()'),
            ('Foobar(a)', 'Foobar(a)'),
            ('(42) Foobar', '⟨42⟩ Foobar'),
            ('( 1) Foobar', '( 1) Foobar'),
            ('(1) Foobar', '⟨1⟩ Foobar'),
            ('Nascar (2016) | Foobar', 'Nascar ⟨2016⟩ | Foobar'),
            ('(1) Fo(1)oba(4000)(c3)r', '⟨1⟩ Fo⟨1⟩oba⟨4000⟩(c3)r'),
            ('1Foobar', '1Foobar'),
            ('Foo bar', 'Foo bar'),
            ('F(00)bar', 'F⟨00⟩bar'),
        )

        for title, expected_result in titles:
            self.assertEqual(self.selenium.execute_script('return notifications_safe_title("%s")' % title), expected_result)

