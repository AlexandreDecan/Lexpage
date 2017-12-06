from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from notifications.models import Notification
from profile.models import ActiveUser
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
        self.assertEqual(str(Slogan.objects.last()), 'Hello Lexpage!')

        self.client.logout()

    def test_list(self):
        response = self.client.get(reverse('slogan_list'))
        self.assertEqual(response.status_code, 200)

    def test_no_slogan(self):
        Slogan.objects.all().delete()
        self.assertEqual(Slogan.visible.get_random(), {'slogan': 'aucun', 'author': 'aucun'})


class SlogansNotificationsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.client.login(username='admin', password='admin')
        self.user = ActiveUser.objects.get(username='admin')
        Notification.objects.all().delete()

        group, _ = Group.objects.get_or_create(name='SloganTeam')
        group.user_set.add(self.user)

    def test_notification_created(self):
        self.assertEqual(Notification.objects.count(), 0)
        slogan = Slogan(author='auteur', slogan='Dura lex sed lex!')
        slogan.save()

        self.assertEqual(Notification.objects.count(), 1)

    def test_notification_deleted_when_approved(self):
        slogan = Slogan(author='auteur', slogan='Dura lex sed lex!')
        slogan.save()
        self.assertEqual(Notification.objects.count(), 1)

        slogan.is_visible = False
        slogan.save()
        self.assertEqual(Notification.objects.count(), 1)

        slogan.is_visible = True
        slogan.save()
        self.assertEqual(Notification.objects.count(), 0)

    def test_notification_deleted_when_deleted(self):
        slogan = Slogan(author='auteur', slogan='Dura lex sed lex!')
        slogan.save()
        self.assertEqual(Notification.objects.count(), 1)

        slogan.delete()
        self.assertEqual(Notification.objects.count(), 0)

