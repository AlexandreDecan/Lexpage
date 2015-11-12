from django.test import TestCase
from django.core.urlresolvers import reverse
from slogan.models import Slogan


class SlogansTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def test_create(self):
        self.client.login(username='user1', password='user1')
        response = self.client.get(reverse('slogan_add'))
        self.assertEqual(response.status_code, 200)

        self.client.post(reverse('slogan_add'), {'slogan': 'Hello Lexpage!'})
        with self.assertRaises(Slogan.DoesNotExist):
            Slogan.visible.get(slogan='Hello Lexpage!')
        self.assertEqual(Slogan.objects.last().slogan, 'Hello Lexpage!')

        self.client.logout()

    def test_list(self):
        response = self.client.get(reverse('slogan_list'))
        self.assertEqual(response.status_code, 200)

