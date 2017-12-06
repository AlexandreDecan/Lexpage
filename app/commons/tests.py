import unittest
import subprocess
import os
import filecmp
import glob
import datetime
from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from .search import SEARCH
from difflib import context_diff
from .templatetags import misc


backup_file = lambda x: '%s.orig' % x


class MarkupViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def test_markuppage_bbcode(self):
        response = self.client.post(reverse('markup_bbcode'))
        self.assertEqual(response.status_code, 200)

    def test_markuppage_markdown(self):
        response = self.client.post(reverse('markup_markdown'))
        self.assertEqual(response.status_code, 200)

    def test_markuppreview_loginrequired(self):
        url = reverse('markup_preview', kwargs={'markup': 'bbcode'})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('auth_login') + '?next=' + url, 302, 200)

    def test_markuppreview_empty(self):
        self.client.login(username='user1', password='user1')
        url = reverse('markup_preview', kwargs={'markup': 'bbcode'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_markuppreview_not_empty(self):
        self.client.login(username='user1', password='user1')
        url = reverse('markup_preview', kwargs={'markup': 'bbcode'})
        response = self.client.post(url, {'content': '[b]Hello World[/b]!'})
        self.assertContains(response, 'Hello World', status_code=200)
        self.client.logout()

    def test_markup_embed(self):
        self.client.login(username='user1', password='user1')
        url = reverse('markup_preview', kwargs={'markup': 'bbcode'})
        response = self.client.post(url, {'content': '[embed]http://lexpage.net[/embed]!'})
        self.assertContains(response, '<a class="oembed" href="http://lexpage.net">http://lexpage.net</a>', status_code=200)
        self.client.logout()


class SearchViewsTests(TestCase):
    fixtures = ['devel']

    def test_searchpage(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)

    def test_emptysearch(self):
        fields = {'query_text': '',
                  'target': 2,  # blogpost
                  'author': '',
                  'date_start': '',
                  'date_end': ''}
        response = self.client.post(reverse('search'), fields)
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        targets = range(len(SEARCH))
        for target in targets:
            fields = {'query_text': 'hello',
                      'target': target,
                      'author': 'world',
                      'date_start': '01/01/14',
                      'date_end': '01/01/15'}
            response = self.client.post(reverse('search'), fields)
            self.assertEqual(response.status_code, 200)


@unittest.skipIf(not settings.RUN_NPM_TESTS, 'Grunt tests are disabled')
class StaticFileTests(TestCase):
    nunjucks_templates = 'app/commons/static/js/nunjucks.templates.js'
    styles = glob.glob('app/commons/static/css/*.css')
    files = [nunjucks_templates] + styles

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        for path in cls.files:
            os.rename(path, backup_file(path))

    @classmethod
    def tearDownClass(cls):
        for path in cls.files:
            os.rename(backup_file(path), path)
        super().tearDownClass()

    def compare_with_backup(self, path):  # pragma: no cover
        samefile = filecmp.cmp(path, backup_file(path), False)
        if not samefile:
            files = []
            for filename in (backup_file(path), path):
                with open(filename) as f:
                    content = f.readlines()
                files.append(content)
            for line in context_diff(*files, fromfile=backup_file(path), tofile=path):
                print(line)
        self.assertTrue(samefile)

    def test_templates_rendered(self):
        grunt = subprocess.call(['grunt', 'nunjucks'])
        self.assertEqual(grunt, 0)
        self.compare_with_backup(self.nunjucks_templates)

    def test_css_rendered(self):
        grunt = subprocess.call(['grunt', 'compass'])
        self.assertEqual(grunt, 0)
        for filename in self.styles:
            self.compare_with_backup(filename)


class ShortTimeSinceTests(TestCase):
    def setUp(self):
        # Because "now()" could change during the execution, let's save an arbitrary date
        self.date = datetime.datetime(year=2017, month=10, day=13)

    def test_values(self):
        delta = [
            (0, '<1m'),
            (1, '<1m'),
            (30, '<1m'),
            (59, '<1m'),
            (60, '1m'),
            (61, '1m'),
            (120, '2m'),
            (121, '2m'),
            (3559, '59m'),
            (3600, '1h'),
            (3600 * 6, '6h'),
            (3600 * 24 - 1, '23h'),
            (3600 * 24, '1j'),
            (3600 * 24 * 15, '15j'),
            (3600 * 24 * 15 - 1, '14j'),
            (3600 * 24 * 15 + 1, '15j'),
            (3600 * 24 * 30 - 1, '29j'),
            (3600 * 24 * 30, '13 sep'),
            (3600 * 24 * 34, '9 sep'),
            (3600 * 24 * 30 * 6, '16 avr'),
            (3600 * 24 * 30 * 12, '18 oct'),
            (3600 * 24 * 30 * 18, 'avr 2016'),
            (3600 * 24 * 30 * 20, 'fév 2016'),  # Check for locale
        ]

        for value, expected in delta:
            with self.subTest():
                result = misc.shorttimesince(self.date - datetime.timedelta(seconds=value), self.date)
                self.assertEqual(result, expected, msg='Testing {} seconds'.format(value))
