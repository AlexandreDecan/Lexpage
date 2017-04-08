from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

import datetime


class ThreadManager(models.Manager):
    def create_thread(self, user, title, text, targets):
        """
        Create a new thread for the given user and the given targets.

        :param user: author of the thread
        :param title: title of the thread (if empty, is autopopulated from involved users)
        :param text: content of the first message
        :param targets: a list of User instances
        :return: newly created MessageBox instance
        """

        # Empty title -> autopopulate!
        if len(title) == 0:
            usernames = [user.get_username()] + [x.get_username() for x in targets]
            usernames.sort()
            title = 'Conversation entre %s et %s' % (', '.join(usernames[:-1]), usernames[-1])

        # Create thread
        thread = Thread(title=title)
        thread.save()   # Needed to have a PK value

        # Create user's message box
        userMBox = MessageBox(user=user, thread=thread)
        userMBox.save()

        # Create MessageBoxes for targets
        for target in targets:
            targetMBox = MessageBox(user=target, thread=thread)
            targetMBox.save()

        # Post message
        thread.post_message(user, text)
        return userMBox


class Thread(models.Model):
    title = models.CharField(verbose_name='Titre', max_length=60)
    last_message = models.ForeignKey('Message', verbose_name='Dernier message', related_name='+', db_constraint=False, default=-1, on_delete=models.CASCADE)

    objects = ThreadManager()

    class Meta:
        get_latest_by = 'last_message'
        ordering = ['-last_message__date']
        verbose_name = 'Conversation'

    def __str__(self):
        return self.title

    @property
    def recipients(self):
        boxes = MessageBox.objects.all().filter(thread=self)
        users = []
        for box in boxes:
            users.append(box.user)
        users.sort(key=lambda x: x.username)
        return users

    @property
    def number(self):
        return Message.objects.all().filter(thread=self).count()

    def post_message(self, user, text):
        """
        Post a message in the current thread and update the MessageBox instances of the participants.
        :param user: author of the new message
        :param text: text of the new message
        :return: user's MessageBox instance
        """
        """ Post a message in the current thread and update
        the MessageBoxes according to their status. 
        Return user's MessageBox. """
        # Create message
        message = Message(author=user, thread=self, text=text)
        message.save()

        self.last_message = message
        self.save()

        # Update MessageBoxes
        message_boxes = MessageBox.objects.filter(thread=self)
        for message_box in message_boxes:
            if message_box.status == MessageBox.STATUS_DELETED:
                message_box.mark_normal()
            elif message_box.status == MessageBox.STATUS_ARCHIVED:
                message_box.mark_normal()
            message_box.save()

        # Update current user MessageBox's date_read
        message_box = MessageBox.objects.get(user=user, thread=self)
        message_box.mark_read()
        message_box.save()

        return message_box


class Message(models.Model):
    author = models.ForeignKey(User, verbose_name='Auteur', related_name='+', on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, verbose_name='Conversation', on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Message')
    date = models.DateTimeField(verbose_name='Date', auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        get_latest_by = 'date'
        ordering = ['date']
        verbose_name = 'Message'


class MessageBoxManager(models.Manager):
    def __init__(self, status):
        super(MessageBoxManager, self).__init__()
        self._status = status

    def get_queryset(self):
        return super(MessageBoxManager, self).get_queryset().filter(status=self._status)


class MessageBox(models.Model):
    DEFAULT_UNREAD_DATE = datetime.datetime(datetime.MINYEAR, 1, 1)

    STATUS_DELETED = -1
    STATUS_NORMAL = 1
    STATUS_ARCHIVED = 2

    STATUS_CHOICES = (
        (STATUS_NORMAL, 'Normal'),
        (STATUS_ARCHIVED, 'Archivée'),
        (STATUS_DELETED, 'Supprimée'),
    )

    user = models.ForeignKey(User, verbose_name='Propriétaire', on_delete=models.CASCADE)
    thread = models.ForeignKey(Thread, verbose_name='Conversation', on_delete=models.CASCADE)
    date_read = models.DateTimeField(verbose_name='Dernière lecture', default=DEFAULT_UNREAD_DATE)
    is_starred = models.BooleanField(verbose_name='Favorites ?', default=False)
    status = models.SmallIntegerField(verbose_name='État', choices=STATUS_CHOICES, default=STATUS_NORMAL)

    objects = models.Manager()
    archived = MessageBoxManager(STATUS_ARCHIVED)
    unarchived = MessageBoxManager(STATUS_NORMAL)

    class Meta:
        ordering = ['-thread__last_message__date']
        verbose_name = 'Boîte de réception'
        verbose_name_plural = 'Boîtes de réceptions'

    def __str__(self):
        return '%s: %s' % (self.user, self.thread)

    @property
    def is_read(self):
        return self.thread.last_message.date <= self.date_read
        
    @property
    def is_archived(self):
        return self.status == MessageBox.STATUS_ARCHIVED

    def mark_read(self):
        self.date_read = now()
        self.save()

    def mark_unread(self):
        self.date_read = MessageBox.DEFAULT_UNREAD_DATE
        self.save()

    def mark_starred(self):
        self.is_starred = True
        self.save()

    def mark_unstarred(self):
        self.is_starred = False
        self.save()

    def mark_normal(self):
        self.status = MessageBox.STATUS_NORMAL
        self.save()

    def mark_archived(self):
        self.status = MessageBox.STATUS_ARCHIVED
        self.save()

    def mark_deleted(self):
        """
        Mark current MessageBox as deleted. If every MessageBox instance related to the thread are deleted,
        then the thread is deleted too.
        :return: None
        """
        # Mark as deleted
        self.is_starred = False
        self.status = MessageBox.STATUS_DELETED
        self.save()

        # Get MessageBoxes
        message_boxes = MessageBox.objects.filter(thread=self.thread)

        # If every authors' MessageBox for this Thread is 
        # STATUS_DELETED, then remove everything related...
        for message_box in message_boxes:
            if message_box.status != MessageBox.STATUS_DELETED:
                return
        # Removing the thread will normally do the job...
        self.thread.delete()
