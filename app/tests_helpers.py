import unittest
from django.test import LiveServerTestCase
from django.utils.module_loading import import_string
from django.conf import settings
from django.core.urlresolvers import reverse

try:
    from selenium.webdriver.support.wait import WebDriverWait
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

if hasattr(settings, 'SELENIUM_WEBDRIVER') and SELENIUM_AVAILABLE:
    WebDriver = import_string(settings.SELENIUM_WEBDRIVER)
else:
    WebDriver = None

def logged_in_test(username='user1', password='user1'):
    def login_required_decorator(function):
        def wrapper(_self, *args, **kwargs):
            _self.login(username, password)
            function(_self, *args, **kwargs)
        return wrapper
    return login_required_decorator

@unittest.skipIf(WebDriver is None, 'Selenium not available or webdriver not configured')
class LexpageTestCase(LiveServerTestCase):
    """LiveServerTestCase with helpers functions (e.g login)"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(1)
        cls.selenium.set_window_size(1280, 1024)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LexpageTestCase, cls).tearDownClass()

    def login(self, username, password):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('auth_login')))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)
        self.selenium.find_element_by_xpath('//button[text()="S\'identifier"]').click()
        WebDriverWait(self.selenium, 1).until(
            lambda driver: driver.find_element_by_xpath('//p[contains(text(),"Bienvenue %s")]' % username))

if __name__ == '__main__':
    # We call that script after the travis build to know which browser has been used
    print('Capabilities for %s' % settings.SELENIUM_WEBDRIVER)
    webdriver = WebDriver()
    capabilities = webdriver.capabilities
    for key, value in capabilities.items():
        print(key, ':', value)
    webdriver.quit()

