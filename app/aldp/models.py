from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

from board.models import Message

class DatestampedWithMessagesAndAuthor(models.Model):
    author = models.ForeignKey(User, verbose_name='Modérateur', related_name='+')
    # TODO: définir ceci en fonction de la date du starting_message
    start_date = models.DateTimeField(verbose_name='Date de démarrage', blank=True, null=True,
                                        db_index=True)
    # TODO: définir ceci en fonction de la date du ending_message
    end_date = models.DateTimeField(verbose_name='Date de fin', blank=True, null=True)
    start_message = models.ForeignKey(Message, verbose_name='Message d\'annonce',
                                         related_name='+', blank=True, null=True)
    end_message = models.ForeignKey(Message, verbose_name='Message de cloture',
                                       related_name='+', blank=True, null=True)
    start_message_template = models.ForeignKey('MessageTemplate', verbose_name='Template utilisé pour l\'annonce',
                                         related_name='+', blank=True, null=True)
    end_message_template = models.ForeignKey('MessageTemplate', verbose_name='Template utilisé pour la clôture',
                                       related_name='+', blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['date_started']

    def start(self):
        if self.start_date is None:
            self.start_date = datetime.now()
            self.save()

    def stop(self):
        if self.end_date is None and self.start_date is not None:
            self.end_date = datetime.now()
            self.save()

class Season(DatestampedWithMessagesAndAuthor):
    number = models.SmallIntegerField(verbose_name='Numéro')
    title = models.CharField(verbose_name='Titre', max_length=80)
    description = models.TextField(verbose_name='Description', help_text='Description de la saison')
    slug = models.SlugField(max_length=90)

    class Meta:
        verbose_name = 'Saison'

    def attach(self, turn):
        """Attach a turn from a season."""
        turn.season = self
        turn.save()

    def detach(self, turn):
        """Detach a turn from a season. Runs clean(), which should delete start and end dates."""
        # TODO Check that there are no attached answers
        # detach devrait être refusé non seulement s'il y a des réponses, mais
        # aussi si start_date est déjà dépassé (condition plus restrictive que
        # la présence de réponses). En effet, une fois la manche "visible"
        # (donc start_date <= now()), il n'y a pas de raison de pouvoir la
        # détacher.

        turn.season = None
        turn.start_date = None
        turn.end_date = None
        turn.save()

    def save(self, *args, **kwargs):
        """
        Override save behavior by computing the value of the slug field.
        """

        self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


class Turn(DatestampedWithMessagesAndAuthor):
    number = models.SmallIntegerField(verbose_name='Numéro', blank=True, null=True)
    title = models.CharField(verbose_name='Titre', max_length=80)
    season = models.ForeignKey('Season', verbose_name='Saison', blank=True, null=True)
    # Todo: check unicity of (Season, Number)
    # Todo: Prevent a turn to be started if another one is started
    # Todo: Ensure turn numbers are right

    class Meta:
        verbose_name = 'Manche'

    def __str__(self):
        if not self.number:
            return '%s (manche détachée)' % self.title
        else:
            return '%s (Saison %s, manche %s)' % (self.number, self.season.number)


class Question(models.Model):
    author = models.ForeignKey(User, related_name='+', verbose_name='Author', blank=True)
    turn = models.ForeignKey(Turn, verbose_name='Manche', blank=True, null=True)
    text = models.CharField(verbose_name='Texte', max_length=80, blank=True)
    # Todo: prevent questions to be changed when they are attached to a started session

    @property
    def season(self):
        return self.turn.season if self.turn else None

    class Meta:
        verbose_name = 'Question'

class Subscription(models.Model):
    """
    Pseudo OneToOne through model between Season and User.
    This class is used to send appropriate notifications to the users.
    """
    season = models.ForeignKey(Season)
    user = models.ForeignKey(User, related_name='+')

    class Meta:
        verbose_name = 'Inscription'

class MessageTemplate(models.Model):
    """A template that can be used for the starting and the ending of turns and seasons."""
    # TODO: Filter in form
    KIND_CHOICES = (
        (0, 'Saison'),
        (1, 'Manche'),
    )

    kind = models.IntegerField(choices=KIND_CHOICES,
                               verbose_name='Type de template')
    name = models.CharField(verbose_name='Nom', max_length=80)
    title = models.CharField(verbose_name='Titre du message', max_length=80, blank=True, null=True,
                             help_text='Uniquement utilisé pour les messages démarrant une saison')
    text = models.TextField(verbose_name='Message', help_text='Mis en page avec le BBCode, plus une subsitition de quelques fieds.')
