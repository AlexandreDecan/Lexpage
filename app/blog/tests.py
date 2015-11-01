from django.core.urlresolvers import reverse
from django.test import TestCase
from blog.models import BlogPost
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
        response = self.client.get(reverse('blog_pending_list'))
        self.assertEqual(response.status_code, 200)


class TagsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        pass

    def test_list(self):
        response = self.client.get(reverse('blog_tags'))
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        url = reverse('blog_tags', kwargs={'taglist': 'ab+cd'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_jsonlist(self):
        response = self.client.get(reverse('blog_tags_json'))
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('blog_tags_json'), {'query': 'hello'})
        self.assertEqual(response.status_code, 200)



