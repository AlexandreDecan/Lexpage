from commons.context_processors import global_settings
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, UserManager
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse


import datetime
import hashlib
import random

try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now


class ActiveUserManager(UserManager):
    def get_queryset(self):
        return super(ActiveUserManager, self).get_queryset().filter(is_active=True)


class ActiveUser(User):
    objects = ActiveUserManager()

    class Meta:
        proxy = True
        get_latest_by = 'date_joined'
        ordering = ['date_joined']
        verbose_name = 'Utilisateur actif'
        verbose_name_plural = 'Utilisateurs actifs'


class ActivationKeyManager(models.Manager):
    """
    Mainly shortcuts
    """

    def activate_user(self, key):
        """
        Activate a user. If the key is not valid or has expired, return
        False, otherwise return the user.
        """
        try:
            activation_key = self.get(key=key)
        except self.model.DoesNotExist:
            return False

        if not activation_key.has_expired():
            user = activation_key.user
            user.is_active = True
            user.save()
            activation_key.delete()
            return user
        return False

    def create_inactive_user(self, username, email, password):
        """
        Create a new user and return a pair user, key.
        """
        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()

        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        key = hashlib.sha1((salt+username).encode('utf-8')).hexdigest()

        activation_key = self.create(user=new_user, key=key)
        return new_user, activation_key

    def delete_expired(self):
        """
        Remove the users and the keys that expired.
        """
        for activation_key in self.all():
            try:
                if activation_key.has_expired():
                    user = activation_key.user
                    if not user.is_active:
                        user.delete()
                        activation_key.delete()
            except User.DoesNotExist:
                activation_key.delete()


class ActivationKey(models.Model):
    user = models.OneToOneField(User)
    key = models.CharField('activation_key', max_length=40)

    objects = ActivationKeyManager()

    class Meta:
        verbose_name = 'Clé d\'activation'
        verbose_name_plural = 'Clés d\'activation'

    def has_expired(self):
        """
        Return true if the current activation key has expired.
        """
        exp_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        return self.user.date_joined + exp_date <= datetime_now()

    def send_activation_email(self):
        """
        Send an email to the user with the activation key. Also returns
        the context of this email (for further use).
        """
        context = {'user': self.user,
                   'activation_key': self.key,
                   'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS}
        context.update(global_settings())

        subject = render_to_string('profile/activation_email_subject.txt', context)
        subject = ''.join(subject.splitlines())
        message = render_to_string('profile/activation_email.txt', context)

        self.user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL)
        return context


class Profile(models.Model):
    THEME_CHOICES = settings.THEMES['ALL']

    GENDER_CHOICES = (
        ('M', 'Homme'),
        ('F', 'Femme'),
        # ('?', 'Inconnu')
    )

    COUNTRY_CHOICES = (
        # (0, 'Inconnue'),
        (1, 'Afghanistan'),
        (2, 'Afrique du Sud'),
        (3, 'Akrotiri'),
        (4, 'Albanie'),
        (5, 'Algérie'),
        (6, 'Allemagne'),
        (7, 'Andorre'),
        (8, 'Angola'),
        (9, 'Anguilla'),
        (10, 'Antarctique'),
        (11, 'Antigua-et-Barbuda'),
        (12, 'Antilles néerlandaises'),
        (13, 'Arabie saoudite'),
        (14, 'Arctic Ocean'),
        (15, 'Argentine'),
        (16, 'Arménie'),
        (17, 'Aruba'),
        (18, 'Ashmore and Cartier Islands'),
        (19, 'Atlantic Ocean'),
        (20, 'Australie'),
        (21, 'Autriche'),
        (22, 'Azerbaïdjan'),
        (23, 'Bahamas'),
        (24, 'Bahreïn'),
        (25, 'Bangladesh'),
        (26, 'Barbade'),
        (27, 'Belau'),
        (28, 'Belgique'),
        (29, 'Belize'),
        (30, 'Bénin'),
        (31, 'Bermudes'),
        (32, 'Bhoutan'),
        (33, 'Biélorussie'),
        (34, 'Birmanie'),
        (35, 'Bolivie'),
        (36, 'Bosnie-Herzégovine'),
        (37, 'Botswana'),
        (38, 'Brésil'),
        (39, 'Brunei'),
        (40, 'Bulgarie'),
        (41, 'Burkina Faso'),
        (42, 'Burundi'),
        (43, 'Cambodge'),
        (44, 'Cameroun'),
        (45, 'Canada'),
        (46, 'Cap-Vert'),
        (47, 'Chili'),
        (48, 'Chine'),
        (49, 'Chypre'),
        (50, 'Clipperton Island'),
        (51, 'Colombie'),
        (52, 'Comores'),
        (53, 'Congo'),
        (54, 'Coral Sea Islands'),
        (55, 'Corée du Nord'),
        (56, 'Corée du Sud'),
        (57, 'Costa Rica'),
        (58, "Côte d'Ivoire"),
        (59, 'Croatie'),
        (60, 'Cuba'),
        (61, 'Danemark'),
        (62, 'Dhekelia'),
        (63, 'Djibouti'),
        (64, 'Dominique'),
        (65, 'Égypte'),
        (66, 'Émirats arabes unis'),
        (67, 'Équateur'),
        (68, 'Érythrée'),
        (69, 'Espagne'),
        (70, 'Estonie'),
        (71, 'États-Unis'),
        (72, 'Éthiopie'),
        (73, 'ex-République yougoslave de Macédoine'),
        (74, 'Finlande'),
        (75, 'France'),
        (76, 'Gabon'),
        (77, 'Gambie'),
        (78, 'Gaza Strip'),
        (79, 'Géorgie'),
        (80, 'Ghana'),
        (81, 'Gibraltar'),
        (82, 'Grèce'),
        (83, 'Grenade'),
        (84, 'Groenland'),
        (85, 'Guam'),
        (86, 'Guatemala'),
        (87, 'Guernsey'),
        (88, 'Guinée'),
        (89, 'Guinée équatoriale'),
        (90, 'Guinée-Bissao'),
        (91, 'Guyana'),
        (92, 'Haïti'),
        (93, 'Honduras'),
        (94, 'Hong Kong'),
        (95, 'Hongrie'),
        (96, 'Ile Bouvet'),
        (97, 'Ile Christmas'),
        (98, 'Ile Norfolk'),
        (99, 'Iles Cayman'),
        (100, 'Iles Cook'),
        (101, 'Iles des Cocos (Keeling)'),
        (102, 'Iles Falkland'),
        (103, 'Iles Féroé'),
        (104, 'Iles Fidji'),
        (105, 'Iles Géorgie du Sud et Sandwich du Sud'),
        (106, 'Iles Heard et McDonald'),
        (107, 'Iles Marshall'),
        (108, 'Iles Pitcairn'),
        (109, 'Iles Salomon'),
        (110, 'Iles Svalbard et Jan Mayen'),
        (111, 'Iles Turks-et-Caicos'),
        (112, 'Iles Vierges américaines'),
        (113, 'Iles Vierges britanniques'),
        (114, 'Inde'),
        (115, 'Indian Ocean'),
        (116, 'Indonésie'),
        (117, 'Iran'),
        (118, 'Iraq'),
        (119, 'Irlande'),
        (120, 'Islande'),
        (121, 'Israël'),
        (122, 'Italie'),
        (123, 'Jamaïque'),
        (124, 'Jan Mayen'),
        (125, 'Japon'),
        (126, 'Jersey'),
        (127, 'Jordanie'),
        (128, 'Kazakhstan'),
        (129, 'Kenya'),
        (130, 'Kirghizistan'),
        (131, 'Kiribati'),
        (132, 'Koweït'),
        (133, 'Laos'),
        (134, 'Lesotho'),
        (135, 'Lettonie'),
        (136, 'Liban'),
        (137, 'Liberia'),
        (138, 'Libye'),
        (139, 'Liechtenstein'),
        (140, 'Lituanie'),
        (141, 'Luxembourg'),
        (142, 'Macao'),
        (143, 'Madagascar'),
        (144, 'Malaisie'),
        (145, 'Malawi'),
        (146, 'Maldives'),
        (147, 'Mali'),
        (148, 'Malte'),
        (149, 'Man, Isle of'),
        (150, 'Mariannes du Nord'),
        (151, 'Maroc'),
        (152, 'Maurice'),
        (153, 'Mauritanie'),
        (154, 'Mayotte'),
        (155, 'Mexique'),
        (156, 'Micronésie'),
        (157, 'Moldavie'),
        (158, 'Monaco'),
        (159, 'Monde'),
        (160, 'Mongolie'),
        (161, 'Monténégro'),
        (162, 'Montserrat'),
        (163, 'Mozambique'),
        (164, 'Namibie'),
        (165, 'Nauru'),
        (166, 'Navassa Island'),
        (167, 'Népal'),
        (168, 'Nicaragua'),
        (169, 'Niger'),
        (170, 'Nigeria'),
        (171, 'Nioué'),
        (172, 'Norvège'),
        (173, 'Nouvelle-Calédonie'),
        (174, 'Nouvelle-Zélande'),
        (175, 'Oman'),
        (176, 'Ouganda'),
        (177, 'Ouzbékistan'),
        (178, 'Pacific Ocean'),
        (179, 'Pakistan'),
        (180, 'Panama'),
        (181, 'Papouasie-Nouvelle-Guinée'),
        (182, 'Paracel Islands'),
        (183, 'Paraguay'),
        (184, 'Pays-Bas'),
        (185, 'Pérou'),
        (186, 'Philippines'),
        (187, 'Pologne'),
        (188, 'Polynésie française'),
        (189, 'Porto Rico'),
        (190, 'Portugal'),
        (191, 'Qatar'),
        (192, 'République centrafricaine'),
        (193, 'République démocratique du Congo'),
        (194, 'République dominicaine'),
        (195, 'République tchèque'),
        (196, 'Roumanie'),
        (197, 'Royaume-Uni'),
        (198, 'Russie'),
        (199, 'Rwanda'),
        (200, 'Sahara occidental'),
        (201, 'Saint-Christophe-et-Niévès'),
        (202, 'Sainte-Hélène'),
        (203, 'Sainte-Lucie'),
        (204, 'Saint-Marin'),
        (205, 'Saint-Pierre-et-Miquelon'),
        (206, 'Saint-Siège'),
        (207, 'Saint-Vincent-et-les-Grenadines'),
        (208, 'Salvador'),
        (209, 'Samoa'),
        (210, 'Samoa américaines'),
        (211, 'Sao Tomé-et-Principe'),
        (212, 'Sénégal'),
        (213, 'Serbie'),
        (214, 'Seychelles'),
        (215, 'Sierra Leone'),
        (216, 'Singapour'),
        (217, 'Slovaquie'),
        (218, 'Slovénie'),
        (219, 'Somalie'),
        (220, 'Soudan'),
        (221, 'Southern Ocean'),
        (222, 'Spratly Islands'),
        (223, 'Sri Lanka'),
        (224, 'Suède'),
        (225, 'Suisse'),
        (226, 'Suriname'),
        (227, 'Swaziland'),
        (228, 'Syrie'),
        (229, 'Tadjikistan'),
        (230, 'Taïwan'),
        (231, 'Tanzanie'),
        (232, 'Tchad'),
        (233, 'Terres australes françaises'),
        (234, "Territoire britannique de l'Océan Indien"),
        (235, 'Thaïlande'),
        (236, 'Timor Oriental'),
        (237, 'Togo'),
        (238, 'Tokélaou'),
        (239, 'Tonga'),
        (240, 'Trinité-et-Tobago'),
        (241, 'Tunisie'),
        (242, 'Turkménistan'),
        (243, 'Turquie'),
        (244, 'Tuvalu'),
        (245, 'Ukraine'),
        (246, 'Union européenne'),
        (247, 'Uruguay'),
        (248, 'Vanuatu'),
        (249, 'Venezuela'),
        (250, 'Viêt Nam'),
        (251, 'Wake Island'),
        (252, 'Wallis-et-Futuna'),
        (253, 'West Bank'),
        (254, 'Yémen'),
        (255, 'Zambie'),
        (256, 'Zimbabwe')
    )

    user = models.OneToOneField(User)
    gender = models.CharField(max_length=1,
                              choices=GENDER_CHOICES,
                              blank=True,
                              verbose_name='Genre')
    country = models.IntegerField(choices=COUNTRY_CHOICES,
                                  blank=True, null=True,
                                  verbose_name='Pays actuel')
    city = models.CharField(max_length=100,
                            blank=True,
                            verbose_name='Ville actuelle',
                            help_text='Visible uniquement par les utilisateurs connectés.')
    website_name = models.CharField(max_length=200,
                                    blank=True,
                                    verbose_name='Nom du site web',
                                    help_text='Cela peut être une page Facebook, un compte Twitter ou votre site personnel.')
    website_url = models.URLField(blank=True,
                                  verbose_name='Adresse du site web',
                                  help_text='L\'adresse doit débuter par http://')
    birthdate = models.DateField(blank=True, null=True,
                                 verbose_name='Date de naissance',
                                 help_text='Visible uniquement par les utilisateurs connectés.')
    avatar = models.URLField(blank=True,
                             verbose_name='Adresse de l\'avatar',
                             help_text='Des exemples d\'avatars sont disponibles sur <a href="http://www.avatarsdb.com">AvatarsDB</a>. '+
                                       'Vous pouvez également utiliser <a href="http://www.gravatar.com">Gravatar</a> pour '+
                                       'héberger et centraliser votre avatar. Vous pouvez également envoyer un avatar '+
                                       'depuis votre disque en utilisant le champ ci-dessous.')
    last_visit = models.DateTimeField(blank=True, null=True,
                                      verbose_name='Dernière visite')
    theme = models.CharField(max_length=16,
                             choices=THEME_CHOICES,
                             blank=True, null=True,
                             verbose_name='Thème',
                             help_text='Laissez vide pour adopter automatiquement le thème du moment.')

    class Meta:
        permissions = (('can_see_details', 'Peut voir les détails des profils'),)
        get_latest_by = 'user__date_joined'
        ordering = ['user__date_joined']

    def get_absolute_url(self):
        return reverse('profile_show', kwargs={'username': self.user.username})

    def get_age(self):
        """ Return the age of the user, or None if birthdate is unset. """
        if self.birthdate:
            # return int(((datetime.date.today() - self.birthdate).days) / 365.2425)
            today = datetime.date.today()
            born = self.birthdate
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        else:
            return None

    def get_birthdate(self):
        """ Return the birthdate BUT at current year.
        This is mainly useful for 'naturalday' filter. """
        return datetime.date(datetime.date.today().year, self.birthdate.month, self.birthdate.day)

    def get_theme(self):
        """ Return the theme for the user or fallback to default theme if
        the theme is unset or has been removed."""
        if self.theme and self.theme in dict(settings.THEMES['ALL']).keys():
            return self.theme
        return settings.THEMES['DEFAULT']
