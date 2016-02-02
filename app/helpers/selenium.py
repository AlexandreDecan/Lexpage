from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from time import sleep

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

__all__ = ['LexpageSeleniumTestCase', 'WebDriverWait', 'EC', 'By']


class LexpageSeleniumTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LexpageSeleniumTestCase, cls).tearDownClass()

    def sleep(self, duration):
        return sleep(duration)

    def go(self, url='', delay=0.5):
        self.selenium.get(self.live_server_url + url)
        self.sleep(delay)

    def logout(self):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('auth_logout')))

    def login(self, username='user1', password='user1', incognito=False):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('auth_login')))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)

        if incognito:
            self.selenium.find_element_by_name('incognito').click()

        self.selenium.find_element_by_xpath('//button[text()="S\'identifier"]').click()

        WebDriverWait(self.selenium, 1).until(
            lambda driver: driver.find_element_by_xpath('//div[contains(.,"Bienvenue %s")]' % username))