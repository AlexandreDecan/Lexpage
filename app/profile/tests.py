from django.core.urlresolvers import reverse
from django.test import TestCase

from profile.models import ActivationKey


class AuthViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def login(self):
        self.client.login(username='user1', password='user1')

    def logout(self):
        self.logout()

    def test_autocomplete_accounts(self):
        url = reverse('auth_list')
        response = self.client.get(url, {'query': 'u'})
        self.assertEqual(response.status_code, 404)

        response = self.client.get(url, {'query': 'user'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user1')

    def test_login(self):
        response = self.client.get(reverse('auth_login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('auth_login'), {'username': 'user1', 'password': 'user1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('_auth_user_id', self.client.session)

    def test_logout(self):
        self.login()
        response = self.client.get(reverse('auth_logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_change_password(self):
        response = self.client.get(reverse('auth_password_change'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_reset_password(self):
        response = self.client.get(reverse('auth_password_reset'), follow=True)
        self.assertEqual(response.status_code, 200)


class RegisterViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def test_register(self):
        response = self.client.get(reverse('registration_register'))
        self.assertEqual(response.status_code, 200)

    def test_register_complete(self):
        response = self.client.get(reverse('registration_activation_complete'))
        self.assertEqual(response.status_code, 200)

    def test_register_failed(self):
        response = self.client.get(reverse('registration_activation_failed'))
        self.assertEqual(response.status_code, 200)

    def test_register_activate(self):
        response = self.client.post(reverse('registration_activate'), {'key': 'error'})
        self.assertRedirects(response, reverse('registration_activation_failed'), target_status_code=200)

        # Create a valid key
        new_user, new_key = ActivationKey.objects.create_inactive_user('new_user', 'new_email', 'new_password')
        response = self.client.post(reverse('registration_activate'), {'key': new_key.key})
        self.assertRedirects(response, reverse('registration_activation_complete'), target_status_code=200)


class ProfileViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.client.login(username='user1', password='user1')

    def test_list(self):
        response = self.client.get(reverse('profile_list'))
        self.assertEqual(response.status_code, 200)

    def test_show(self):
        response = self.client.get(reverse('profile_show', kwargs={'username': 'user1'}))
        self.assertEqual(response.status_code, 200)

    def test_edit(self):
        response = self.client.get(reverse('profile_edit'))
        self.assertEqual(response.status_code, 200)
