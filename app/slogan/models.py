from django.db import models


class SloganManager(models.Manager):
    def get_random(self):
        try:
            return self.get_queryset().order_by('?')[0]
        except IndexError: 
            return {'slogan': 'aucun', 'author': 'aucun'}

    def get_queryset(self):
        return super(SloganManager, self).get_queryset().filter(is_visible=True)


class Slogan(models.Model):
    author = models.CharField(max_length=50,
                              verbose_name='Auteur')
    slogan = models.TextField(verbose_name='Slogan')
    date = models.DateField(verbose_name='Date d\'ajout', auto_now_add=True)
    is_visible = models.BooleanField(verbose_name='Visible ?', default=False)
    
    objects = models.Manager()
    visible = SloganManager()

    def __str__(self):
        return self.slogan

    class Meta:
        permissions = (('can_set_visible', 'Peut rendre visible'), )
