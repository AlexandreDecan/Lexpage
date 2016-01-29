import unittest
import time
import os

from django.test import LiveServerTestCase
from django.utils.module_loading import import_string
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import connection
from django.core.servers.basehttp import WSGIServer
from django.test.testcases import LiveServerThread, QuietWSGIRequestHandler, _StaticFilesHandler

from ws4redis.django_runserver import _websocket_url, _websocket_app, _django_app

from socketserver import ThreadingMixIn

from helpers.redis import get_redis_publisher
redis_publisher = get_redis_publisher()


###### Selenium setup

try:
    from selenium.webdriver.support.wait import WebDriverWait
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

if getattr(settings, 'SELENIUM_WEBDRIVER', None) and SELENIUM_AVAILABLE:
    WebDriver = import_string(settings.SELENIUM_WEBDRIVER)
else:
    WebDriver = None


###### Webserver classes

def application(environ, start_response):
    if _websocket_url and environ.get('PATH_INFO').startswith(_websocket_url):
        return _websocket_app(environ, start_response)
    return _StaticFilesHandler(_django_app)(environ, start_response)


class MultiThreadLiveServerThread(LiveServerThread):
    """
    Thread for running a live multithread http server while the tests are running.
    """

    def _create_server(self, port):
        httpd_cls = type('WSGIServer', (ThreadingMixIn, WSGIServer), {'daemon_threads': True})
        return httpd_cls((self.host, port), QuietWSGIRequestHandler)


class MultiThreadLiveServerTestCase(LiveServerTestCase):
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


###### decorators

def logged_in_test(username='user1', password='user1', incognito=None):
    def decorator(function):
        def wrapper(_self, *args, **kwargs):
            _self.login(username, password, incognito)
            function(_self, *args, **kwargs)
        return wrapper
    return decorator


def without_redis():
    def decorator(function):
        def wrapper(_self, *args, **kwargs):
            _self.stop_redis()
            function(_self, *args, **kwargs)
            _self.start_redis()
        return wrapper
    return decorator


###### Functions

def sqlite_sleep(sleeptime):
    if connection.vendor == 'sqlite':
        time.sleep(sleeptime)

###### Test classes


@unittest.skipIf(WebDriver is None, 'Selenium not available or webdriver not configured')
class LexpageTestCase(MultiThreadLiveServerTestCase):
    """LiveServerTestCase with helpers functions (e.g login)"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(1)
        cls.selenium.set_window_size(1280, 1024)
        cls.server_thread.httpd.set_app(application)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LexpageTestCase, cls).tearDownClass()

    def skip_without_redis_commands(self):
        for attr in ('START', 'STOP'):
            if getattr(settings, '%s_REDIS_COMMAND' % attr, None) is None:
                self.skipTest('%s_REDIS_COMMAND should be defined in settings.' % attr)

    def start_redis(self):
        redis_connection = redis_publisher()._connection
        if hasattr(redis_connection, '_start_redis'): # we're using redislite
            redis_connection._start_redis()
            print('REDIS STARTED')
            time.sleep(5)
        elif settings.START_REDIS_COMMAND is not None:
            self.skip_without_redis_commands()
            os.system(settings.START_REDIS_COMMAND)

    def stop_redis(self):
        redis_connection = redis_publisher()._connection
        if hasattr(redis_connection, '_start_redis'): # we're using redislite
            redis_connection.shutdown()
        elif settings.STOP_REDIS_COMMAND is not None:
            self.skip_without_redis_commands()
            os.system(settings.STOP_REDIS_COMMAND)

    def logout(self):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('auth_logout')))

    def login(self, username, password, incognito=None):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('auth_login')))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(password)
        if incognito is None:
            incognito = connection.vendor == 'sqlite'
        if not incognito and connection.vendor == 'sqlite':
            self.skipTest('This test requires a connection without incognito mode. It is not possible with sqlite.')
        if incognito:
            self.selenium.find_element_by_name('incognito').click()
        self.selenium.find_element_by_xpath('//button[text()="S\'identifier"]').click()
        WebDriverWait(self.selenium, 1).until(
            lambda driver: driver.find_element_by_xpath('//div[contains(.,"Bienvenue %s")]' % username))

