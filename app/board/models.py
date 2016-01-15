import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django.utils.text import slugify

from blog.models import BlogPost

import difflib


USE_DIFF_FOR_HISTORY = True


class Thread(models.Model):
    title = models.CharField(verbose_name='Titre', max_length=80)
    slug = models.SlugField(max_length=90, unique=False)
    number = models.IntegerField(verbose_name='Nombre de messages', default=0)
    date_created = models.DateTimeField(verbose_name='Date de création', auto_now_add=True)
    last_message = models.ForeignKey('Message', verbose_name='Dernier message', db_constraint=False, related_name='+', default=-1)

    class Meta:
        get_latest_by = 'date_created'
        ordering = ['date_created']
        verbose_name = 'Discussion'

    def get_absolute_url(self):
        return reverse('board_thread_show', kwargs={'thread': self.pk})

    def annotate_flag(self, user):
        """
        Annotate the current Thread by adding the related Flag object (if it
        exists for given user) as a `flag` attribute.
        :param user: Related user
        :return: None
        """
        if not user.is_authenticated():
            return
        try:
            self.flag = Flag.objects.all().get(thread=self, user=user)
        except Flag.DoesNotExist:
            pass

    def save(self, *args, **kwargs):
        # Slug handler
        self.slug = slugify(self.title)
        return super(Thread, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def authors(self, N=None):
        """
        Return an ordered list of N first authors.
        """
        authors = Message.objects.all().filter(thread=self).order_by('date').values_list('author')
        tmp_set = set()
        # http://stackoverflow.com/questions/6197409/ordered-sets-python-2-7
        output = [User.objects.all().get(pk=x[0]) for x in authors
                  if x[0] not in tmp_set and not tmp_set.add(x[0])]
        if N is None:
            return output
        else:
            return output[:N]

    def post_message(self, user, text):
        """
        Post a new message in this thread.
        :param user: Author of the message.
        :param text: Text content.
        :return: The newly created Message instance.
        """
        # Create a new message
        message = Message(author=user, thread=self, text=text)
        message.save()

        # Update last message
        self.last_message = message
        self.number = self.number + 1
        self.save()

        return message


class Message(models.Model):
    author = models.ForeignKey(User, verbose_name='Auteur', related_name='board_post')
    thread = models.ForeignKey(Thread, verbose_name='Sujet')
    text = models.TextField(verbose_name='Message', help_text='Mis en page avec le BBCode.')
    moderated = models.BooleanField(verbose_name='Message modéré ?', default=False,
                                    help_text='Si le message est modéré, son auteur ne pourra plus le modifier.')
    date = models.DateTimeField(verbose_name='Date', auto_now_add=True)

    class Meta:
        get_latest_by = 'date'
        ordering = ['date']
        verbose_name = 'Message'
        permissions = (('can_moderate', 'Peut modérer'),
                       ('can_destroy', 'Peut détruire'))

    def get_absolute_url(self):
        return reverse('board_message_show', kwargs={'message': self.pk})

    def __str__(self):
        return self.text[:50] + "..."

    def position(self):
        """
        Return the relative position in the thread, 0-indexed.
        """
        return Message.objects.all().filter(thread=self.thread, date__lt=self.date).count()

    def is_time_to_delete(self):
        """
        Return True iff message can be deleted, this is, if message is at most 5 minutes old and if
        message is not moderated.
        :return: Boolean
        """
        return not self.moderated and (datetime.datetime.now() - self.date).total_seconds() <= 5 * 60

    def delete(self, **kwargs):
        """
        Remove given message from thread. If this is the only message in the
        thread, remove the thread. Update flags. Return previous message, or
        None
        :param **kwargs:
        """
        if self.thread.number == 1:
            # Delete thread (and by cascade, this message)
            self.thread.delete()
            return None
        else:
            # Get previous message
            previous = self.previous()
            # If there is no previous, then remove the flags
            if previous is None:
                Flag.objects.all().filter(thread=self.thread, message=self).delete()
                anchor = next(self)
            else:
                anchor = previous
                # Update flags
                Flag.objects.all().filter(thread=self.thread, message=self).update(message=previous)

                # Update last_message, if needed
                if self.thread.last_message == self:
                    self.thread.last_message = previous

            self.thread.number = self.thread.number - 1
            self.thread.save()

            # Remove message
            super(Message, self).delete()
            return anchor

    def previous(self):
        """
        Return the previous message, or None.
        """
        try:
            return Message.objects.all().filter(thread=self.thread, date__lt=self.date).latest()
        except Message.DoesNotExist:
            return None

    def __next__(self):
        """
        Return the next message, or None.
        """
        try:
            return Message.objects.all().filter(thread=self.thread, date__gt=self.date)[0]
        except IndexError:
            return None

    def modify(self, author, text):
        """
        Edit current message and create a MessageHistory instance.
        """
        if USE_DIFF_FOR_HISTORY:
            diff = difflib.unified_diff(self.text.splitlines(),
                text.splitlines(),
                fromfile='ancien',
                tofile='nouveau',
                n=0,
                lineterm='')
            ntext = '\n'.join([str(x) for x in diff])
        else:
            ntext = self.text

        msg_hist = MessageHistory(message=self, edited_by=author, text=ntext)
        msg_hist.save()
        self.text = text
        self.save()

    def last_modified(self):
        """
        Return the last modification.
        """
        return MessageHistory.objects.all().filter(message=self).latest('date')

    def number_modified(self):
        """
        Return the number of times this message was modified.
        """
        return MessageHistory.objects.all().filter(message=self).count()


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, verbose_name='Message', related_name='history')
    edited_by = models.ForeignKey(User, verbose_name='Auteur de la modification', related_name='+')
    date = models.DateTimeField(verbose_name='Date', auto_now_add=True)
    text = models.TextField(verbose_name='Historique')

    class Meta:
        get_latest_by = 'date'
        ordering = ['date']
        verbose_name = 'Édition de message'
        verbose_name_plural = 'Éditions de message'


class FlagManager(models.Manager):
    def read(self, user, message, force=False):
        """
        Look for a Flag and create if needed. Update the message if newer, or
        if force is True. Return the flag.
        """
        if not user.is_authenticated():
            return
        flag, created = self.get_or_create(user=user, thread=message.thread, defaults={'message': message})
        # Only update if needed or wanted
        if force or (flag.message.date < message.date):
            flag.message = message
            flag.save()
        return flag

    def unread(self, user, message):
        """
        Set message as the first unread message on the thread. Remove the flag
        if message is the first of the thread.
        """
        thread = message.thread
        try:
            flag = self.all().get(user=user, thread=thread)
        except Flag.DoesNotExist:
            # No flag, do nothing
            return None

        previous = message.previous()
        if previous:
            # Update the flag
            flag.message = previous
            flag.save()
        else:
            # Remove the flag
            flag.delete()


class Flag(models.Model):
    user = models.ForeignKey(User, verbose_name='Auteur', related_name='+')
    thread = models.ForeignKey(Thread, verbose_name='Sujet')
    message = models.ForeignKey(Message, verbose_name='Dernier message lu')

    objects = FlagManager()

    class Meta:
        verbose_name = 'Suivi'
        unique_together = (('user', 'thread'),)


class BlogBoardLink(models.Model):
    """
    Pseudo OneToOne through model between BlogPost and Thread.
    This class is used to make a direct link when a Thread is created
    for a BlogPost.
    """
    thread = models.OneToOneField(Thread)
    post = models.OneToOneField(BlogPost)
