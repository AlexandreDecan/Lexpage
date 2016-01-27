from django.core.urlresolvers import reverse
from django.test import TestCase

from profile.models import Profile


class AuthViewsTests(TestCase):
    fixtures = ['devel']

    def test_login_incognito(self):
        last_visit_before_login = Profile.objects.get(user__username='user1').last_visit
        response = self.client.get(reverse('auth_login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('auth_login'), {'username': 'user1', 'password': 'user1', 'incognito': 'on'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('incognito', self.client.session)
        self.assertEqual(self.client.session['incognito'], True)
        last_visit_after_login = Profile.objects.get(user__username='user1').last_visit
        self.assertEqual(last_visit_before_login, last_visit_after_login)
        self.assertContains(response, 'class="avatar incognito" title="Mode incognito"')
        self.assertNotContains(response, 'online_init_ping')

    def test_login_not_incognito(self):
        last_visit_before_login = Profile.objects.get(user__username='user1').last_visit
        response = self.client.get(reverse('auth_login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('auth_login'), {'username': 'user1', 'password': 'user1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('incognito', self.client.session)
        self.assertEqual(self.client.session['incognito'], False)
        last_visit_after_login = Profile.objects.get(user__username='user1').last_visit
        self.assertNotEqual(last_visit_before_login, last_visit_after_login)
        self.assertNotContains(response, 'class="avatar incognito" title="Mode incognito"')
        self.assertContains(response, 'online_init_ping')


