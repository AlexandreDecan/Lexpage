from contextlib import contextmanager
from unittest import skipIf

from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse

from time import sleep
from django.utils.module_loading import import_string
from django.test import LiveServerTestCase
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions

__all__ = ['LexpageSeleniumTestCase', 'WebDriverWait', 'EC', 'By', 'exceptions']


@skipIf(not getattr(settings, 'SELENIUM_WEBDRIVER', None), 'Selenium webdriver is not defined')
class LexpageSeleniumTestCase(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = import_string(settings.SELENIUM_WEBDRIVER)()
        cls.timeout = 10

        # Reset cache
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LexpageSeleniumTestCase, cls).tearDownClass()

    def sleep(self, duration):
        return sleep(duration)

    def go(self, url=''):
        self.selenium.get(self.live_server_url + url)

    def logout(self):
        self.go(reverse('auth_logout'))

    def login(self, username='user1', password='user1', incognito=False):
        self.go(reverse('auth_login'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)

        if incognito:
            self.selenium.find_element_by_name('incognito').click()

        with self.wait_for_page_load():
            self.selenium.find_element_by_xpath('//button[text()="S\'identifier"]').click()

        try:
            element = self.selenium.find_element_by_css_selector('.form .alert.alert-danger')
            raise AssertionError('Cannot login: ' + element.text)
        except exceptions.NoSuchElementException:
            pass

        WebDriverWait(self.selenium, self.timeout).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.contrib-messages .alert'), 'Bienvenue')
        )

    @contextmanager
    def wait_for_page_load(self, timeout=None):
        old_page = self.selenium.find_element_by_tag_name('html')
        yield
        WebDriverWait(self.selenium, timeout or self.timeout).until(
            EC.staleness_of(old_page)
        )