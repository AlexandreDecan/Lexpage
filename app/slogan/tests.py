from django.test import TestCase
from django.core.urlresolvers import reverse


class ViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def test_sloganaddpage_login_required(self):
        url = reverse('slogan_add')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('auth_login') + '?next=' + url, 302, 200)

    def test_sloganaddpage_login(self):
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('slogan_add'))
        self.assertEqual(response.status_code, 200)
        self.client.logout()

    def test_sloganlistpage(self):
        response = self.client.get(reverse('slogan_list'))
        self.assertEqual(response.status_code, 200)
