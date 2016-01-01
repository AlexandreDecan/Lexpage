from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

from board.models import Thread, Message
from blog.models import BlogPost
from profile.models import ActiveUser

from tests_helpers import LexpageTestCase, login_required
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from board.tests_data import fable, formatted_message
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class ThreadViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.client.login(username='user1', password='user1')
        self.threads = Thread.objects.filter(number__gt=10)

    def test_threadlist(self):
        urls = [
            'board_latests',
            'board_archives',
            'board_archives_messages',
            'board_followed',
            'board_followed_unread',
        ]
        for url in urls:
            response = self.client.get(reverse(url))
            self.assertEqual(response.status_code, 200, url)

    def test_threadcreate(self):
        response = self.client.get(reverse('board_create'))
        self.assertEqual(response.status_code, 200)
        nb_threads = Thread.objects.count()
        response = self.client.post(reverse('board_create'), {'title': 'Hello World!',
                                                              'text': 'Hello World!'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Thread.objects.count(), nb_threads + 1)

    def test_threadcreateforpost(self):
        post = BlogPost.published.latest()
        url = reverse('board_create_for_post', kwargs={'post': post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_threadpost(self):
        old_message = self.threads[0].last_message
        self.threads[0].post_message(ActiveUser.objects.get(username='user1'), 'Hello World!')
        self.threads[0].refresh_from_db()
        self.assertNotEqual(self.threads[0].last_message, old_message)

    def test_threadrss(self):
        response = self.client.get(reverse('board_rss'))
        self.assertEqual(response.status_code, 200)

    def test_threadshow(self):
        urls = [
            'board_thread_show',
            'board_thread_show_last',
            'board_thread_show_unread',
        ]
        for url in urls:
            reversed_url = reverse(url, kwargs={'thread': self.threads[0].pk})
            response = self.client.get(reversed_url, follow=True)
            self.assertEqual(response.status_code, 200, url)

    def test_threadreply(self):
        url = reverse('board_thread_reply', kwargs={'thread': self.threads[0].pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_threadmarkunread(self):
        url = reverse('board_thread_mark_unread', kwargs={'thread': self.threads[0].pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_deletemessage(self):
        # Log as admin
        self.client.login(username='admin', password='admin')
        user = ActiveUser.objects.get(username='admin')

        # Create dummy thread
        thread = Thread(title='Hello World!')
        thread.save()
        msg1 = thread.post_message(user, 'Hello 1')
        msg2 = thread.post_message(user, 'Hello 2')

        # Remove second message
        response = self.client.get(reverse('board_message_delete', kwargs={'message': msg2.pk}), follow=True)
        self.assertEqual(response.status_code, 200)

        thread.refresh_from_db()
        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(pk=msg2.pk)
        self.assertEqual(thread.last_message, msg1)

        # Remove first (and last) message
        response = self.client.get(reverse('board_message_delete', kwargs={'message': msg1.pk}))
        self.assertRedirects(response, reverse('board_latests'))

        with self.assertRaises(Message.DoesNotExist):
            Message.objects.get(pk=msg1.pk)
        with self.assertRaises(Thread.DoesNotExist):
            Thread.objects.get(pk=thread.pk)


class MessageViewsTests(TestCase):
    fixtures = ['devel']

    def setUp(self):
        self.client.login(username='user1', password='user1')
        self.messages = Message.objects.filter(author=ActiveUser.objects.filter(username='user1'))

    def test_messageshow(self):
        url = reverse('board_message_show', kwargs={'message': self.messages[0].pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_messageedit(self):
        message = self.messages[0]

        url = reverse('board_message_edit', kwargs={'message': message.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {'text': 'Hello World!'}, follow=True)
        message.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.text, 'Hello World!')

    def test_messagemoderate(self):
        message = self.messages[0]
        self.client.login(username='admin', password='admin')

        url = reverse('board_message_moderate', kwargs={'message': message.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {'text': 'Hello World!', 'moderated': True}, follow=True)
        message.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.text, 'Hello World!')
        self.assertEqual(message.moderated, True)

    def test_markunread(self):
        url = reverse('board_message_mark_unread', kwargs={'message': self.messages[0].pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_raw(self):
        url = reverse('board_message_raw', kwargs={'message': self.messages[0].pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

class BoardsBrowserTests(LexpageTestCase):
    fixtures = ['devel']

    @login_required()
    def test_can_post_a_message(self):
        lexpagiens_link = self.selenium.find_element_by_link_text('Discussions')
        ActionChains(self.selenium).move_to_element(lexpagiens_link).perform()
        disconnect_link = self.selenium.find_element_by_link_text('Nouvelle discussion')
        disconnect_link.click()
        WebDriverWait(self.selenium, 1).until(
            lambda driver: driver.find_element_by_id('id_title'))
        # le Corbeau et le Renard, Jean de la Fontaine
        title = 'Le corbeau et le renard'
        title_input = self.selenium.find_element_by_name('title')
        title_input.send_keys(title)
        text_input = self.selenium.find_element_by_name('text')
        text_input.send_keys(fable)
        self.selenium.find_element_by_css_selector('.fa.fa-bold').click()
        text_input.send_keys('Et du GRAS!')
        for i in range(len('[/b]')):
            text_input.send_keys(Keys.RIGHT)
        self.selenium.find_element_by_css_selector('.fa.fa-italic').click()
        text_input.send_keys('Et de l\'italique!')
        for i in range(len('[/i]')):
            text_input.send_keys(Keys.LEFT)

        self.selenium.find_element_by_xpath('//button[text()="Poster"]').click()
        WebDriverWait(self.selenium, 1).until(
            lambda driver: driver.find_element_by_xpath('//h3[text()="%s"]' % title))

        text_block = self.selenium.find_element_by_css_selector('.board-messagelist .message-text .bbcode')
        self.maxDiff = 4096
        self.assertEqual(text_block.get_attribute('innerHTML').strip(), formatted_message)


    @login_required()
    def test_can_delete_a_thread(self):
        Thread.objects.all().delete()
        thread = Thread(title='Test thread', slug='test-thread')
        thread.save()
        message = thread.post_message(User.objects.get(username='user1'), 'foo')
        message.save()
        self.selenium.refresh()
        self.selenium.find_element_by_link_text('Test thread').click()
        self.selenium.find_element_by_css_selector('span.fa.fa-trash-o').click()
        WebDriverWait(self.selenium, 1).until(
            EC.visibility_of_element_located((By.ID, 'confirm-action-yes')))
        self.selenium.find_element_by_id('confirm-action-yes').click()
        alert_texts = []
        for alert in self.selenium.find_elements_by_css_selector('.messages .alert'):
            alert_texts.append(alert.text.strip())
        wanted_text = ['Le message a été supprimé.', 'La discussion étant vide, elle a été supprimée également.']
        self.assertEqual(alert_texts, wanted_text)
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_link_text('Test thread')

