from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from blog.models import BlogPost
from board.models import Thread, Message


class ViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def test_homepage(self):
        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_no_blogpost(self):
        # Remove existing blog posts
        BlogPost.objects.all().delete()

        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['post_list']), 0)

    def test_no_thread(self):
        # Remove existing threads
        Thread.objects.all().delete()

        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['threads'].object_list), 0)

    def test_recent_thread(self):
        # Remove existing threads
        Thread.objects.all().delete()
        thread = Thread(title='Test thread', slug='test-thread')
        thread.save()
        Message(author=User.objects.get(username='user1'), thread=thread, text='foo').save()

        response = self.client.get(reverse('homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['threads'].object_list), 1)
