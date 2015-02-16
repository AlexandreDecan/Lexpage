# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivationKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=40, verbose_name='activation_key')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
                'verbose_name': "Cl\xe9 d'activation",
                'verbose_name_plural': "Cl\xe9s d'activation",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gender', models.CharField(blank=True, max_length=1, verbose_name='Genre', choices=[('M', 'Homme'), ('F', 'Femme')])),
                ('country', models.IntegerField(blank=True, null=True, verbose_name='Pays actuel', choices=[(1, 'Afghanistan'), (2, 'Afrique du Sud'), (3, 'Akrotiri'), (4, 'Albanie'), (5, 'Alg\xe9rie'), (6, 'Allemagne'), (7, 'Andorre'), (8, 'Angola'), (9, 'Anguilla'), (10, 'Antarctique'), (11, 'Antigua-et-Barbuda'), (12, 'Antilles n\xe9erlandaises'), (13, 'Arabie saoudite'), (14, 'Arctic Ocean'), (15, 'Argentine'), (16, 'Arm\xe9nie'), (17, 'Aruba'), (18, 'Ashmore and Cartier Islands'), (19, 'Atlantic Ocean'), (20, 'Australie'), (21, 'Autriche'), (22, 'Azerba\xefdjan'), (23, 'Bahamas'), (24, 'Bahre\xefn'), (25, 'Bangladesh'), (26, 'Barbade'), (27, 'Belau'), (28, 'Belgique'), (29, 'Belize'), (30, 'B\xe9nin'), (31, 'Bermudes'), (32, 'Bhoutan'), (33, 'Bi\xe9lorussie'), (34, 'Birmanie'), (35, 'Bolivie'), (36, 'Bosnie-Herz\xe9govine'), (37, 'Botswana'), (38, 'Br\xe9sil'), (39, 'Brunei'), (40, 'Bulgarie'), (41, 'Burkina Faso'), (42, 'Burundi'), (43, 'Cambodge'), (44, 'Cameroun'), (45, 'Canada'), (46, 'Cap-Vert'), (47, 'Chili'), (48, 'Chine'), (49, 'Chypre'), (50, 'Clipperton Island'), (51, 'Colombie'), (52, 'Comores'), (53, 'Congo'), (54, 'Coral Sea Islands'), (55, 'Cor\xe9e du Nord'), (56, 'Cor\xe9e du Sud'), (57, 'Costa Rica'), (58, "C\xf4te d'Ivoire"), (59, 'Croatie'), (60, 'Cuba'), (61, 'Danemark'), (62, 'Dhekelia'), (63, 'Djibouti'), (64, 'Dominique'), (65, '\xc9gypte'), (66, '\xc9mirats arabes unis'), (67, '\xc9quateur'), (68, '\xc9rythr\xe9e'), (69, 'Espagne'), (70, 'Estonie'), (71, '\xc9tats-Unis'), (72, '\xc9thiopie'), (73, 'ex-R\xe9publique yougoslave de Mac\xe9doine'), (74, 'Finlande'), (75, 'France'), (76, 'Gabon'), (77, 'Gambie'), (78, 'Gaza Strip'), (79, 'G\xe9orgie'), (80, 'Ghana'), (81, 'Gibraltar'), (82, 'Gr\xe8ce'), (83, 'Grenade'), (84, 'Groenland'), (85, 'Guam'), (86, 'Guatemala'), (87, 'Guernsey'), (88, 'Guin\xe9e'), (89, 'Guin\xe9e \xe9quatoriale'), (90, 'Guin\xe9e-Bissao'), (91, 'Guyana'), (92, 'Ha\xefti'), (93, 'Honduras'), (94, 'Hong Kong'), (95, 'Hongrie'), (96, 'Ile Bouvet'), (97, 'Ile Christmas'), (98, 'Ile Norfolk'), (99, 'Iles Cayman'), (100, 'Iles Cook'), (101, 'Iles des Cocos (Keeling)'), (102, 'Iles Falkland'), (103, 'Iles F\xe9ro\xe9'), (104, 'Iles Fidji'), (105, 'Iles G\xe9orgie du Sud et Sandwich du Sud'), (106, 'Iles Heard et McDonald'), (107, 'Iles Marshall'), (108, 'Iles Pitcairn'), (109, 'Iles Salomon'), (110, 'Iles Svalbard et Jan Mayen'), (111, 'Iles Turks-et-Caicos'), (112, 'Iles Vierges am\xe9ricaines'), (113, 'Iles Vierges britanniques'), (114, 'Inde'), (115, 'Indian Ocean'), (116, 'Indon\xe9sie'), (117, 'Iran'), (118, 'Iraq'), (119, 'Irlande'), (120, 'Islande'), (121, 'Isra\xebl'), (122, 'Italie'), (123, 'Jama\xefque'), (124, 'Jan Mayen'), (125, 'Japon'), (126, 'Jersey'), (127, 'Jordanie'), (128, 'Kazakhstan'), (129, 'Kenya'), (130, 'Kirghizistan'), (131, 'Kiribati'), (132, 'Kowe\xeft'), (133, 'Laos'), (134, 'Lesotho'), (135, 'Lettonie'), (136, 'Liban'), (137, 'Liberia'), (138, 'Libye'), (139, 'Liechtenstein'), (140, 'Lituanie'), (141, 'Luxembourg'), (142, 'Macao'), (143, 'Madagascar'), (144, 'Malaisie'), (145, 'Malawi'), (146, 'Maldives'), (147, 'Mali'), (148, 'Malte'), (149, 'Man, Isle of'), (150, 'Mariannes du Nord'), (151, 'Maroc'), (152, 'Maurice'), (153, 'Mauritanie'), (154, 'Mayotte'), (155, 'Mexique'), (156, 'Micron\xe9sie'), (157, 'Moldavie'), (158, 'Monaco'), (159, 'Monde'), (160, 'Mongolie'), (161, 'Mont\xe9n\xe9gro'), (162, 'Montserrat'), (163, 'Mozambique'), (164, 'Namibie'), (165, 'Nauru'), (166, 'Navassa Island'), (167, 'N\xe9pal'), (168, 'Nicaragua'), (169, 'Niger'), (170, 'Nigeria'), (171, 'Niou\xe9'), (172, 'Norv\xe8ge'), (173, 'Nouvelle-Cal\xe9donie'), (174, 'Nouvelle-Z\xe9lande'), (175, 'Oman'), (176, 'Ouganda'), (177, 'Ouzb\xe9kistan'), (178, 'Pacific Ocean'), (179, 'Pakistan'), (180, 'Panama'), (181, 'Papouasie-Nouvelle-Guin\xe9e'), (182, 'Paracel Islands'), (183, 'Paraguay'), (184, 'Pays-Bas'), (185, 'P\xe9rou'), (186, 'Philippines'), (187, 'Pologne'), (188, 'Polyn\xe9sie fran\xe7aise'), (189, 'Porto Rico'), (190, 'Portugal'), (191, 'Qatar'), (192, 'R\xe9publique centrafricaine'), (193, 'R\xe9publique d\xe9mocratique du Congo'), (194, 'R\xe9publique dominicaine'), (195, 'R\xe9publique tch\xe8que'), (196, 'Roumanie'), (197, 'Royaume-Uni'), (198, 'Russie'), (199, 'Rwanda'), (200, 'Sahara occidental'), (201, 'Saint-Christophe-et-Ni\xe9v\xe8s'), (202, 'Sainte-H\xe9l\xe8ne'), (203, 'Sainte-Lucie'), (204, 'Saint-Marin'), (205, 'Saint-Pierre-et-Miquelon'), (206, 'Saint-Si\xe8ge'), (207, 'Saint-Vincent-et-les-Grenadines'), (208, 'Salvador'), (209, 'Samoa'), (210, 'Samoa am\xe9ricaines'), (211, 'Sao Tom\xe9-et-Principe'), (212, 'S\xe9n\xe9gal'), (213, 'Serbie'), (214, 'Seychelles'), (215, 'Sierra Leone'), (216, 'Singapour'), (217, 'Slovaquie'), (218, 'Slov\xe9nie'), (219, 'Somalie'), (220, 'Soudan'), (221, 'Southern Ocean'), (222, 'Spratly Islands'), (223, 'Sri Lanka'), (224, 'Su\xe8de'), (225, 'Suisse'), (226, 'Suriname'), (227, 'Swaziland'), (228, 'Syrie'), (229, 'Tadjikistan'), (230, 'Ta\xefwan'), (231, 'Tanzanie'), (232, 'Tchad'), (233, 'Terres australes fran\xe7aises'), (234, "Territoire britannique de l'Oc\xe9an Indien"), (235, 'Tha\xeflande'), (236, 'Timor Oriental'), (237, 'Togo'), (238, 'Tok\xe9laou'), (239, 'Tonga'), (240, 'Trinit\xe9-et-Tobago'), (241, 'Tunisie'), (242, 'Turkm\xe9nistan'), (243, 'Turquie'), (244, 'Tuvalu'), (245, 'Ukraine'), (246, 'Union europ\xe9enne'), (247, 'Uruguay'), (248, 'Vanuatu'), (249, 'Venezuela'), (250, 'Vi\xeat Nam'), (251, 'Wake Island'), (252, 'Wallis-et-Futuna'), (253, 'West Bank'), (254, 'Y\xe9men'), (255, 'Zambie'), (256, 'Zimbabwe')])),
                ('city', models.CharField(max_length=100, verbose_name='Ville actuelle', blank=True)),
                ('website_name', models.CharField(help_text='Cela peut \xeatre une page Facebook, un compte Twitter ou votre site personnel.', max_length=200, verbose_name='Nom du site web', blank=True)),
                ('website_url', models.URLField(help_text="L'adresse doit d\xe9buter par http://", verbose_name='Adresse du site web', blank=True)),
                ('birthdate', models.DateField(null=True, verbose_name='Date de naissance', blank=True)),
                ('avatar', models.URLField(help_text='Des exemples d\'avatars sont disponibles sur <a href="http://www.avatarsdb.com">AvatarsDB</a>. Vous pouvez \xe9galement utiliser <a href="http://www.gravatar.com">Gravatar</a> pour h\xe9berger et centraliser votre avatar. Vous pouvez \xe9galement envoyer un avatar depuis votre disque en utilisant le champ ci-dessous.', verbose_name="Adresse de l'avatar", blank=True)),
                ('last_visit', models.DateTimeField(null=True, verbose_name='Derni\xe8re visite', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user__date_joined'],
                'get_latest_by': 'user__date_joined',
                'permissions': (('can_see_details', 'Peut voir les d\xe9tails des profils'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ActiveUser',
            fields=[
            ],
            options={
                'ordering': ['date_joined'],
                'get_latest_by': 'date_joined',
                'verbose_name': 'Utilisateur actif',
                'proxy': True,
                'verbose_name_plural': 'Utilisateurs actifs',
            },
            bases=('auth.user',),
        ),
    ]
