#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

from django.core.urlresolvers import reverse

from django.utils.text import slugify

import math

POST_ICONS = {
    'achat': 'fa-shopping-cart',
    'actualité': 'fa-flash',
    'argent': 'fa-money',
    'amour': 'fa-heart',
    'android': 'fa-mobile',
    'animaux': 'fa-bug',
    'animation': 'fa-film',
    'archive': 'fa-archive',
    'astuces': 'fa-key',
    'bd': 'fa-comment-o',
    'bière': 'fa-beer', 
    'blague': 'fa-smile-o',
    'bouffe': 'fa-cutlery',
    'cadeau': 'fa-gift',
    'calendrier': 'fa-calendar',
    'carte': 'fa-map-marker',
    'casse-tête': 'fa-puzzle-piece',
    'citation': 'fa-quote-right',
    'clavier': 'fa-keyboard-o',
    'code': 'fa-code',
    'coeur': 'fa-heart',
    'court-métrage': 'fa-film',
    'date': 'fa-calendar',
    'download': 'fa-download',
    'économie': 'fa-money',
    'énigme': 'fa-puzzle-piece',
    'femme': 'fa-female',
    'film': 'fa-film',
    'geek': 'fa-laptop',
    'graphique': 'fa-bar-chart-o',
    'homme': 'fa-male',
    'humour': 'fa-smile-o',
    'ios': 'fa-mobile',
    'ipad': 'fa-tablet',
    'iphone': 'fa-mobile',
    'image': 'fa-picture-o',
    'internet': 'fa-globe',
    'jeu': 'fa-gamepad',
    'lecture': 'fa-book',
    'livre': 'fa-book',
    'maison': 'fa-home',
    'mobile': 'fa-mobile',
    'monde': 'fa-globe',
    'musique': 'fa-music',
    'nourriture': 'fa-cutlery',
    'p2p': 'fa-exchange',
    'pc': 'fa-desktop',
    'people': 'fa-group',
    'photo': 'fa-camera',
    'réseau': 'fa-signal',
    'sciences': 'fa-flask',
    'smartphone': 'fa-mobile',
    'statistique' : 'fa-bar-chart-o',
    'tablette': 'fa-tablet',
    'téléchargement': 'fa-download',
    'téléphone': 'fa-phone',
    'terre': 'fa-globe',
    'vidéo': 'fa-video-camera',
    'voyage': 'fa-plane',
    'wifi': 'fa-signal',
}


class PostManager(models.Manager):
    def __init__(self, status, ordering):
        super(PostManager, self).__init__()
        self._status = status
        self._ordering = ordering

    def get_queryset(self):
        return super(PostManager, self).get_queryset().filter(status=self._status).order_by(*self._ordering)

    def get_tags_list(self, sort_name=False, relative=True):
        """
        Return a list of every tag already used in a post, with the 
        number of posts having this tag. The resulting structure is 
        ordered by this number, except if sort_name is True. 
        If relative is True, then the number will be a percentage wrt. the most
        viewed tag. Otherwise, the number will be a simple count.
        """
        if sort_name == False:
            sort_name = lambda x: -x[1]
        else:
            sort_name = lambda x: x[0]

        posts = self.all()
        count = {}

        for post in posts:
            for tag in post.tags_list():
                count[tag] = count.setdefault(tag, 0) + 1

        if relative:
            for k,v in count.items():
                count[k] = int(100*math.log10(v))

        ordered_count = count.items()
        ordered_count.sort(key=sort_name)
        return ordered_count


class BlogPost(models.Model):
    STATUS_DRAFT = 1
    STATUS_SUBMITTED = 2
    STATUS_APPROVED = 3
    STATUS_PUBLISHED = 4
    STATUS_HIDDEN = 5

    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Brouillon'),
        (STATUS_SUBMITTED, 'Proposé'),
        (STATUS_APPROVED, 'Validé'), 
        (STATUS_PUBLISHED, 'Publié'),
        (STATUS_HIDDEN, 'Masqué')
    )

    PRIORITY_VERY_HIGH = 1
    PRIORITY_HIGH = 2
    PRIORITY_NORMAL = 5
    PRIORITY_LOW = 8
    PRIORITY_VERY_LOW = 14

    PRIORITY_CHOICES = (
        (PRIORITY_VERY_HIGH, 'Urgente'), 
        (PRIORITY_HIGH, 'Haute'), 
        (PRIORITY_NORMAL, 'Normale'), 
        (PRIORITY_LOW, 'Faible'),
        (PRIORITY_VERY_LOW, 'Très faible')
    )

    title = models.CharField(verbose_name='Titre', max_length=100)
    slug = models.SlugField(max_length=120, unique=False)
    tags = models.CharField(verbose_name='Étiquettes', max_length=100, blank=True, help_text='Étiquettes associées, séparées par un espace.')
    abstract = models.TextField(verbose_name='Chapeau', help_text='Mis en page avec Markdown.')
    text = models.TextField(verbose_name='Contenu', help_text='Mis en page avec Markdown.', blank=True)
    author = models.ForeignKey(User, verbose_name='Auteur', )
    date_created = models.DateTimeField(verbose_name='Date de création', auto_now_add=True)
    approved_by = models.ForeignKey(User, verbose_name='Validateur', blank=True, null=True, related_name='+')
    date_approved = models.DateTimeField(verbose_name='Date de validation', blank=True, null=True)
    date_published = models.DateTimeField(verbose_name='Date de publication', blank=True, null=True)
    date_modified = models.DateTimeField(verbose_name='Date de dernière modification', blank=True, null=True, auto_now=True)
    priority = models.SmallIntegerField(verbose_name='Priorité', choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL)
    status = models.SmallIntegerField(verbose_name='État', choices=STATUS_CHOICES, default=STATUS_DRAFT)

    objects = models.Manager()
    drafts = PostManager(STATUS_DRAFT, ('-date_created',))
    submitted = PostManager(STATUS_SUBMITTED, ('priority', 'date_created'))
    approved = PostManager(STATUS_APPROVED, ('priority', 'date_created',))
    published = PostManager(STATUS_PUBLISHED, ('date_published',))

    def get_absolute_url(self):
        return reverse('blog_post_show', kwargs={'pk': self.pk})

    def get_icon(self):
        """
        Return the first icon that can be associated to a tag. 
        """
        tags = self.tags_list()
        for tag in tags:
            if tag in POST_ICONS:
                return POST_ICONS[tag]
        return 'fa-chevron-right'

    def get_next(self):
        """ Return the next post by date_published, only for 
        published post. """
        try:
            return BlogPost.published.filter(date_published__gt=self.date_published).order_by('date_published')[0]
        except IndexError:
            pass

    def get_previous(self):
        """ Return the previous post by date_published, only for
        published post. """
        try:
            return BlogPost.published.filter(date_published__lt=self.date_published).order_by('-date_published')[0]
        except IndexError:
            pass


    def change_status(self, user, new_status):
        """ 
        Change the current status according to the new status.
        """
        if new_status == BlogPost.STATUS_DRAFT:
            self.author = user

        if self.status < BlogPost.STATUS_SUBMITTED and new_status >= BlogPost.STATUS_SUBMITTED:
            self.date_created = now()

        if self.status < BlogPost.STATUS_APPROVED and new_status >= BlogPost.STATUS_APPROVED:
            self.approved_by = user
            self.date_approved = now()

        if self.status < BlogPost.STATUS_PUBLISHED and new_status >= BlogPost.STATUS_PUBLISHED:
            self.date_published = now()


        self.status = new_status
        self.save()

    def save(self, *args, **kwargs):
        # Slug handler
        self.slug = slugify(self.title)
        return super(BlogPost, self).save(*args, **kwargs)

    def tags_list(self):
        """ Return a list of tags. """
        return [unicode(x) for x in self.tags.split(' ') if len(x) > 0]

    def __unicode__(self):
        return unicode(self.title)

    class Meta():
        get_latest_by = 'date_published'
        ordering = ['-date_published']
        verbose_name = 'Billet'
        permissions = (('can_approve', 'Peut valider'),)

