from django.core.urlresolvers import reverse
from django.test import TestCase
from blog.models import BlogPost
from blog.forms import UserCreatePostForm
from profile.models import ActiveUser
import datetime


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
        self.client.login(username='admin', password='admin')
        self.user = ActiveUser.objects.filter(username='admin')[0]
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
            'priority': self.post.priority
        }

    def test_draft(self):
        self.form['action'] = UserCreatePostForm.ACTION_DRAFT
        response = self.client.post(self.url, self.form, follow=True)
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual((datetime.datetime.now() - self.post.date_modified).total_seconds(), 10)

    def test_submitted(self):
        self.post.status = BlogPost.STATUS_DRAFT
        self.post.save()

        self.form['action'] = UserCreatePostForm.ACTION_SUBMIT
        response = self.client.post(self.url, self.form, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_approved(self):
        self.form['action'] = UserCreatePostForm.ACTION_APPROVE
        response = self.client.post(self.url, self.form, follow=True)
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual((datetime.datetime.now() - self.post.date_approved).total_seconds(), 10)

    def test_published(self):
        self.form['action'] = UserCreatePostForm.ACTION_PUBLISH
        response = self.client.post(self.url, self.form, follow=True)
        self.post.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual((datetime.datetime.now() - self.post.date_published).total_seconds(), 10)

    def test_reject(self):
        self.form['action'] = UserCreatePostForm.ACTION_DELETE
        response = self.client.post(self.url, self.form, follow=True)
        self.assertEqual(response.status_code, 200)


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

    def test_jsonlist(self):
        response = self.client.get(reverse('blog_tags_json'))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('blog_tags_json'), {'query': 'hello'})
        self.assertEqual(response.status_code, 200)

    def test_jsonsearch(self):
        url = reverse('blog_tags', kwargs={'taglist': 'ab+cd'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

