from django.core.servers.basehttp import WSGIServer
from django.test.testcases import LiveServerThread, QuietWSGIRequestHandler
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse

from socketserver import ThreadingMixIn
from ws4redis.django_runserver import _websocket_url, _websocket_app, _django_app
from whitenoise.django import DjangoWhiteNoise

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

def application(environ, start_response):
    if _websocket_url and environ.get('PATH_INFO').startswith(_websocket_url):
        return _websocket_app(environ, start_response)
    return DjangoWhiteNoise(_django_app)(environ, start_response)


def login_required(username='user1', password='user1', displayed_username=None):
    if displayed_username is None:
        displayed_username = username
    def login_required_decorator(function):
        def wrapper(_self, *args, **kwargs):
            _self.login(username, password, displayed_username)
            function(_self, *args, **kwargs)
            _self.logout()
        return wrapper
    return login_required_decorator


class MultiThreadLiveServerThread(LiveServerThread):
    """
    Thread for running a live multithread http server while the tests are running.
    """

    def _create_server(self, port):
        httpd_cls = type('WSGIServer', (ThreadingMixIn, WSGIServer), {'daemon_threads': True})
        return httpd_cls((self.host, port), QuietWSGIRequestHandler)


class MultiThreadLiveServerTestCase(StaticLiveServerTestCase):
    """ This class extends the StaticLiveServerTestCase with a webserver that supports
    multithreading."""

    @classmethod
    def _create_server_thread(cls, host, possible_ports, connections_override):
        return MultiThreadLiveServerThread(
            host,
            possible_ports,
            cls.static_handler,
            connections_override=connections_override,
        )


class LexpageTestCase(MultiThreadLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(5)
        cls.selenium.set_window_size(1280, 1024)
        super(LexpageTestCase, cls).setUpClass()
        cls.server_thread.httpd.set_app(application)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LexpageTestCase, cls).tearDownClass()

    def go_to_login_form(self):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('auth_login')))

    def fill_in_login_form(self, username, password):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('auth_login')))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)
        self.selenium.find_element_by_xpath('//button[text()="S\'identifier"]').click()

    def login(self, username, password, displayed_username=None):
        if displayed_username is None:
            displayed_username = username
        self.go_to_login_form()
        self.fill_in_login_form(username, password)
        WebDriverWait(self.selenium, 20).until(
            lambda driver: driver.find_element_by_xpath('//p[contains(text(),"Bienvenue %s")]' % displayed_username))

    def logout(self):
        lexpagiens_link = self.find_link_with_icon('Lexpagiens')
        ActionChains(self.selenium).move_to_element(lexpagiens_link).perform()
        disconnect_link = self.find_link_with_icon('Se déconnecter')
        disconnect_link.click()
        WebDriverWait(self.selenium, 2).until(
            lambda driver: driver.find_element_by_xpath('//p[text()=\'Vous êtes maintenant déconnecté de votre compte. \']'))

    def login_failure(self, username, password):
        self.go_to_login_form()
        error_message = 'Erreur lors de la validation'
        error_message_xpath = '//strong[text()="%s"]' % error_message
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath(error_message_xpath)
        self.fill_in_login_form(username, password)
        self.selenium.find_element_by_xpath(error_message_xpath)

    def wait_for_minichat_ready(self):
        disabled_input = '//p[text()[contains(.,"Connexion...")]]'
        WebDriverWait(self.selenium, 60).until_not(
            lambda driver: driver.find_element_by_xpath(disabled_input))

    def check_notification_count(self, count):
        notif_xpath = '//span[@class="fa fa-bell" and contains(text(),"%s")]' % count
        WebDriverWait(self.selenium, 5).until(
            lambda driver: driver.find_element_by_xpath(notif_xpath))
