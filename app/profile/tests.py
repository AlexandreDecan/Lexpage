from django.core.urlresolvers import reverse
from django.test import TestCase

from profile.models import ActivationKey, Profile, User


def user1_login():
    def decorator(fct):
        def wrapper(_self, *args, **kwargs):
            _self.client.login(username='user1', password='user1')
            fct(_self, *args, **kwargs)
        return wrapper
    return decorator


class AuthViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def login(self):
        self.client.login(username='user1', password='user1')

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

    def test_login_case_insensitive(self):
        response = self.client.get(reverse('auth_login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('auth_login'), {'username': 'User1', 'password': 'user1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_password_case_insensitive(self):
        response = self.client.get(reverse('auth_login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('auth_login'), {'username': 'user1', 'password': 'User1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_nonexistent_user(self):
        response = self.client.get(reverse('auth_login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('auth_login'), {'username': 'user2', 'password': 'user2'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_case_insensitive(self):
        response = self.client.get(reverse('auth_login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('auth_login'), {'username': 'User1', 'password': 'user1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_password_case_insensitive(self):
        response = self.client.get(reverse('auth_login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('auth_login'), {'username': 'user1', 'password': 'User1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_nonexistent_user(self):
        response = self.client.get(reverse('auth_login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('auth_login'), {'username': 'user2', 'password': 'user2'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)


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

        profile = Profile.objects.get(user__username='user1')

        form = {
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'email': 'test@test.test',
            'gender': Profile.GENDER_CHOICES[0][0],
            'country': Profile.COUNTRY_CHOICES[0][0],
            'city': 'hello',
            'website_name': 'Lexpage',
            'website_url': 'http://www.lexpage.net',
            'birthdate': '01/01/1970',
        }
        response = self.client.post(reverse('profile_edit'), form)
        self.assertRedirects(response, reverse('profile_edit'))

        profile.refresh_from_db()
        # Check only some field.
        self.assertEqual(profile.city, 'hello')
        self.assertEqual(profile.website_name, 'Lexpage')


class AutocompleteTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        for username in ('user2', 'user3'):
            User.objects.create_user(
                username=username, email='%s@example.com' % username, password='top_secret')

    def test_403_without_login(self):
        response = self.client.get(reverse('profile_api_list'), {'query': 'adm'}, format='json')
        self.assertEqual(response.status_code, 403)

    @user1_login()
    def test_partial_anchor(self):
        response = self.client.get(reverse('profile_api_list'), {'query': 'adm'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': 'adm', 'suggestions': ['admin']}, response.data)

    @user1_login()
    def test_partial_anchor_and_multiple_answers(self):
        response = self.client.get(reverse('profile_api_list'), {'query': 'use'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': 'use', 'suggestions': ['user1', 'user2', 'user3']}, response.data)

    @user1_login()
    def test_full_anchor(self):
        response = self.client.get(reverse('profile_api_list'), {'query': 'user2'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': 'user2', 'suggestions': ['user2']}, response.data)

    @user1_login()
    def test_small_anchor(self):
        response = self.client.get(reverse('profile_api_list'), {'query': 'u'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': 'u', 'suggestions': []}, response.data)

    @user1_login()
    def test_no_user_anchor(self):
        response = self.client.get(reverse('profile_api_list'), {'query': 'youpla'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': 'youpla', 'suggestions': []}, response.data)

    @user1_login()
    def test_no_query(self):
        response = self.client.get(reverse('profile_api_list'), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': None, 'suggestions': []}, response.data)

    @user1_login()
    def test_partial_anchor_with_at(self):
        response = self.client.get(reverse('profile_api_list'), {'query': '@adm', 'prefix': '@'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': '@adm', 'suggestions': ['@admin']}, response.data)

    @user1_login()
    def test_partial_anchor_with_at_and_multiple_responses(self):
        response = self.client.get(reverse('profile_api_list'), {'query': '@use', 'prefix': '@'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': '@use', 'suggestions': ['@user1', '@user2', '@user3']}, response.data)

    @user1_login()
    def test_full_anchor_with_at(self):
        response = self.client.get(reverse('profile_api_list'), {'query': '@user2', 'prefix': '@'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': '@user2', 'suggestions': ['@user2']}, response.data)

    @user1_login()
    def test_small_anchor_with_at(self):
        response = self.client.get(reverse('profile_api_list'), {'query': '@u', 'prefix': '@'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': '@u', 'suggestions': []}, response.data)

    @user1_login()
    def test_no_user_anchor_with_at(self):
        response = self.client.get(reverse('profile_api_list'), {'query': '@youpla', 'prefix': '@'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': '@youpla', 'suggestions': []}, response.data)

    @user1_login()
    def test_no_query_with_at(self):
        response = self.client.get(reverse('profile_api_list'), {'prefix': '@'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': None, 'suggestions': []}, response.data)

    @user1_login()
    def test_query_not_starting_with_prefix(self):
        """If a query does not start with the prefix, we should return 400 (bad request)"""
        response = self.client.get(reverse('profile_api_list'), {'query': 'user1', 'prefix': '@'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_403_even_when_query_not_starting_with_prefix(self):
        """If a query does not start with the prefix BUT the user is not authenticated, we should return 403 and not 400"""
        response = self.client.get(reverse('profile_api_list'), {'query': 'user1', 'prefix': '@'}, format='json')
        self.assertEqual(response.status_code, 403)

