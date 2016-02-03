import datetime
import time

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from helpers.selenium import *


class NotificationsSeleniumTests(LexpageSeleniumTestCase):
    def wait_for_notifications_refresh(self):
        self.selenium.execute_script('app_notifications.reset();')
        WebDriverWait(self.selenium, self.timeout).until_not(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.notification_list'))
        )
        self.selenium.execute_script('app_notifications.refresh();')
        WebDriverWait(self.selenium, self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.notification_list'))
        )

    def wait_for_notifications(self):
        WebDriverWait(self.selenium, self.timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.notification_list'))
        )


class NotificationsDisplayTests(NotificationsSeleniumTests):
    def test_existing_notifications_displayed(self):
        pass

    def test_new_notifications_displayed_when_no_notifications(self):
        pass

    def test_new_notifications_displayed_when_existing_notifications(self):
        pass

    def test_notifications_timeout(self):
        pass


class NotificationsDismissTests(NotificationsSeleniumTests):
    def test_dismiss_one_notification(self):
        pass

    def test_dismiss_all_notifications(self):
        pass



