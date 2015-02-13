#!/usr/bin/python
# coding=utf-8

from __future__ import unicode_literals

from django.db import models

class SloganManager(models.Manager):
    def get_random(self):
        try:
            return self.get_query_set().order_by('?')[0]
        except IndexError: 
            return {'slogan': 'aucun', 'author': 'aucun'}

    def get_query_set(self):
        return super(SloganManager, self).get_query_set().filter(is_visible=True)


class Slogan(models.Model):
    author = models.CharField(max_length=50,
                           verbose_name='Auteur')
    slogan = models.TextField(verbose_name='Slogan')
    date = models.DateField(verbose_name='Date d\'ajout', auto_now_add=True)
    is_visible = models.BooleanField(verbose_name='Visible ?', default=False)
    
    objects = models.Manager()
    visible = SloganManager()

    def __unicode__(self):
        return self.slogan

    class Meta():
        permissions = (('can_set_visible', 'Peut rendre visible'), )
