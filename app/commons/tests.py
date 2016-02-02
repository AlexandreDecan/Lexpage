import unittest
import subprocess
import os
import filecmp
import glob
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.conf import settings
from .search import SEARCH
from difflib import context_diff

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


