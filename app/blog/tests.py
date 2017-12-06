from django.contrib.auth.models import Group
from django.urls import reverse
from django.test import TestCase
from blog.models import BlogPost
from blog.forms import UserCreatePostForm
from notifications.models import Notification
from profile.models import ActiveUser


class PostsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.client.login(username='user1', password='user1')
        self.posts = BlogPost.published.all()

    def test_list(self):
        response = self.client.get(reverse('blog_archives'), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_rss(self):
        response = self.client.get(reverse('blog_rss'))
        self.assertEqual(response.status_code, 200)

    def test_show(self):
        url = reverse('blog_post_show', kwargs={'pk': self.posts[0].pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class LoginPostsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.client.login(username='user1', password='user1')
        self.user = ActiveUser.objects.filter(username='user1')[0]
        self.posts = BlogPost.published.all()

    def test_comment(self):
        url = reverse('blog_post_comments', kwargs={'pk': self.posts[0].pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_draflist(self):
        response = self.client.get(reverse('blog_draft_list'))
        self.assertEqual(response.status_code, 200)

    def test_draftcreate(self):
        response = self.client.get(reverse('blog_draft_create'))
        self.assertEqual(response.status_code, 200)

        form = {
            'title': 'Hello World!',
            'tags': 'hello world',
            'abstract': 'Hello World!',
            'text': 'Hello World!',
            'priority': BlogPost.PRIORITY_NORMAL,
            'action': UserCreatePostForm.ACTION_SUBMIT
        }
        response = self.client.post(reverse('blog_draft_create'), form, follow=True)
        self.assertEqual(response.status_code, 200)
        post = BlogPost.submitted.last()
        self.assertEqual(post.title, 'Hello World!')

    def test_drafedit(self):
        post = BlogPost(title='Hello World!',
                        author=self.user,
                        tags='hello world',
                        abstract='Hello World!',
                        text='Hello World!',
                        priority=BlogPost.STATUS_DRAFT)
        post.save()

        url = reverse('blog_draft_edit', kwargs={'pk': post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # Flatpages are not stored in devel fixtures
    #def test_drafhelp(self):
    #    response = self.client.get(reverse('blog_draft_help'))
    #    self.assertEqual(response.status_code, 200)


class StatusTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        Notification.objects.all().delete()
        admin = ActiveUser.objects.get(username='admin')
        group, _ = Group.objects.get_or_create(name='BlogTeam')
        group.user_set.add(admin)

        self.client.login(username='user1', password='user1')
        self.user = ActiveUser.objects.filter(username='user1')[0]
        self.post = BlogPost(title='Hello World!',
                             author=self.user,
                             tags='hello world',
                             abstract='Hello World!',
                             text='Hello World!',
                             priority=BlogPost.PRIORITY_NORMAL)
        self.post.save()

        self.url = reverse('blog_pending_edit', kwargs={'pk': self.post.pk})
        self.form = {
            'title': self.post.title,
            'abstract': self.post.abstract,
            'tags': self.post.tags,
            'text': self.post.text,
            'priority': self.post.priority,
            'action': UserCreatePostForm.ACTION_DRAFT,
        }

    def test_draft(self):
        self.form['action'] = UserCreatePostForm.ACTION_DRAFT
        response = self.client.post(self.url, self.form, follow=True)
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Notification.objects.all()), 0)

    def test_submit(self):
        self.form['action'] = UserCreatePostForm.ACTION_SUBMIT
        response = self.client.post(self.url, self.form, follow=True)
        self.assertEqual(response.status_code, 200)
        Notification.objects.get(recipient__username='admin')

        self.client.login(username='admin', password='admin')
        self.form['action'] = UserCreatePostForm.ACTION_APPROVE
        response = self.client.post(self.url, self.form, follow=True)
        self.assertEqual(response.status_code, 200)
        Notification.objects.get(recipient__username='user1')
        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(recipient__username='admin')

    def test_published(self):
        self.form['action'] = UserCreatePostForm.ACTION_PUBLISH
        response = self.client.post(self.url, self.form, follow=True)
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(Notification.objects.all()), 0)

    def test_reject(self):
        self.form['action'] = UserCreatePostForm.ACTION_SUBMIT
        response = self.client.post(self.url, self.form, follow=True)
        self.assertEqual(response.status_code, 200)
        Notification.objects.get(recipient__username='admin')

        self.client.login(username='admin', password='admin')
        self.form['action'] = UserCreatePostForm.ACTION_DELETE
        response = self.client.post(self.url, self.form, follow=True)
        self.assertEqual(response.status_code, 200)
        Notification.objects.get(recipient__username='user1')
        with self.assertRaises(Notification.DoesNotExist):
            Notification.objects.get(recipient__username='admin')


class PendingTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.client.login(username='admin', password='admin')
        self.user = ActiveUser.objects.filter(username='admin')[0]
        self.post = BlogPost(title='Hello World!',
                             author=self.user,
                             tags='hello world',
                             abstract='Hello World!',
                             text='Hello World!',
                             priority=BlogPost.STATUS_SUBMITTED)
        self.post.save()

    def test_list(self):
        response = self.client.get(reverse('blog_pending_list'))
        self.assertEqual(response.status_code, 200)

    def test_edit(self):
        url = reverse('blog_pending_edit', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TagsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def test_list(self):
        response = self.client.get(reverse('blog_tags'))
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        response = self.client.post(reverse('blog_tags'), {'tags': 'hello'}, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_jsonsearch(self):
        url = reverse('blog_tags', kwargs={'taglist': 'ab+cd'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AutocompleteTests(TestCase):
    fixtures = ['devel']

    def test_400_without_query(self):
        response = self.client.get(reverse('blog_api_tags'), format='json')
        self.assertEqual(response.status_code, 400)

    def test_partial_anchor(self):
        response = self.client.get(reverse('blog_api_tags'), {'query': 'je'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': 'je', 'suggestions': [{'data': 1, 'value': 'jeu'}]}, response.data)

    def test_full_anchor(self):
        response = self.client.get(reverse('blog_api_tags'), {'query': 'humour'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': 'humour', 'suggestions': [{'data': 1, 'value': 'humour'}]}, response.data)

    def test_no_results(self):
        response = self.client.get(reverse('blog_api_tags'), {'query': 'graveleux'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual({'query': 'graveleux', 'suggestions': []}, response.data)
