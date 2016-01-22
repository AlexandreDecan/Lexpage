# Lexpage v4 [![Build Status](https://travis-ci.org/AlexandreDecan/Lexpage.svg?branch=master)](https://travis-ci.org/AlexandreDecan/Lexpage)  [![Coverage Status](https://coveralls.io/repos/AlexandreDecan/Lexpage/badge.svg?branch=master&service=github)](https://coveralls.io/github/AlexandreDecan/Lexpage?branch=master)

Bienvenue sur le dépôt *officiel* du Lexpage ! 

Ce dépôt contient le code source de la v4 du [Lexpage](http://www.lexpage.net).
Il s'agit essentiellement d'un ensemble de petites applications Django ainsi que des templates et les fichiers statiques
associés pour faire tourner le site. 

Certains fichiers (avatars, configuration en prod, flatpages, sniffer de la NSA, etc.) ne sont pas présents sur
le dépôt pour des raisons évidentes qu'il ne faut bien entendu pas vous détailler.

La suite de ce README s'organise ainsi : 
 - Une description rapide de ce que contient le dépôt. 
 - Des explications pour pouvoir builder et tester ce qui s'y trouve.
 - Des informations sur la manière de contribuer.
 
Bonne lecture !


## Que contient le dépôt ?

Le répertoire */app* contient tout ce qui est propre à Django et au Lexpage : 
 - Les répertoires *blog*, *board*, *commons*, *messaging*, *minichat*, *notifications*, *profile* et *slogan*
   contiennent les applications.
 - Les répertoires *media*, *media_pub*, *static*, *static_pub* contiennent les fichiers statiques. *media* et
   *media_pub* ne sont pas utilisés. Le dossier *static_pub* sert à accueillir les fichiers statiques collectés
   automatiquement depuis les sous-répertoires *static* des différentes applications. C'est aussi dans ce dossier
   que sont uploadés les avatars des utilisateurs. 
 - Le répertoire *templates* contient les templates globales du site. Les sous-répertoires *templates* des différentes
   applications contiennent les templates spécifiques
   à chaque application.
 - Le fichier *settings_common.py* contient les paramètres de base, quelque soit l'environnement.
 - Le fichier *settings_dev.py* contient les paramètres de développement, et doivent être utilisés en local.
   Il charge automatiquement tout ce qui se trouve dans *settings_common.py*.
 - Le fichier *settings_travis.py* contient des éléments spécifiques pour la mise en plus du CI Travis.
 - Le reste est classique pour du Django.
  
La racine du dépôt contient notamment :
 - *requirements_common.txt* contient les dépendances communes aux différents environnements.
 - *requirements_dev.txt* contient les dépendances pour le développement et les tests.
   Il charge automatiquement les dépendances de *requirements_common.txt*.
 - *requirements_prod.txt* contient les dépendances supplémentaires pour la production.
 
 
## Comment tester localement ?

Tester localement le site se fait de manière assez simple, pour peu que vous sachiez suivre une documentation :-)

### Mettre en place un environnement virtuel

Que vous utilisiez `docker`, `vagrant` ou `virtualenv`, l'important est d'isoler votre environnement.
Lexpage nécessite Python 3.4 ou supérieur pour fonctionner, ainsi qu'une petite liste de dépendances que
vous retrouverez dans le fichier *requirements.txt*.

Si vous avez Python 3.4 (ou supérieur) sur votre système, c'est très simple :
 - On commence par installer de quoi gérer un environnement virtuel : `pip install virtualenv` (droits d'administrateur
 requis sauf si vous installez localement, consultez la documentation de `pip`)
 - On crée l'environnement : `virtualenv venv -p python3.4` va créer un environnement avec Python 3.4 dedans,
   dans le répertoire *venv*.
 - On saute dedans avec `source venv/bin/activate`
 - On installe les dépendances avec `pip install -r requirements_dev.txt`
 - Et on a terminé !

Vous pouvez utiliser le serveur de développement de Django pour tester le site:
`python app/manage.py runserver --settings=settings_dev`

### Configurer et utiliser Django pour servir Lexpage

Avant de pouvoir tester le site, il y a quelques opérations à faire :

#### Mettre en place la base de données

Par défaut, la configuration de développement travaille avec SQLite. En production, nous tournons avec Postgresql.
Si vous n'aimez pas SQLite ou que vous voulez utiliser autre chose, pensez à adapter le fichier de configuration.
Dans tous les cas, si c'est la première fois que vous lancez le site, il faudra créer la base de données :
`python app/manage.py migrate --settings=settings_dev`

Cette commande va simplement exécuter les requêtes nécessaires à la création des tables.
Si vous avez déjà une base de données pré-remplies, elle devrait normalement (et sous réserve de toute bonne volonté
de la part de l'ORM) être mise à jour automatiquement. Croisez les doigts pour vos données.

A ce stade, une base va être créée et contiendra les différents modèles. La base est globalement vide.
Des données de test sont fournies dans le répertoire `app/fixtures/`.
Vous pouvez notamment charger ces données automatiquement dans la base de données via :
`python app/manage.py loaddata devel --settings=settings_dev`

Si vous ne souhaitez pas utiliser ces données, mais que vous voulez tester l'authentification et ces machins-là sur
le site, il vous faudra au moins un compte administrateur. Utilisez donc Django pour ça :
`python app/manage.py createsuperuser`
Cette commande va vous permettre de créer un compte administrateur, étape indispensable pour pouvoir vous logguer et,
si nécessaire, créer d'autres utilisateurs, et ainsi de suite.

#### Mettre en place les fichiers statiques

Enfin, afin que le site puisse fournir les fichiers statiques nécessaires à son affichage et à son fonctionnement,
il convient d'indiquer à Django de collecter ces fichiers statiques depuis les différentes applications qui sont
utilisées, et de les réunir dans un répertoire qui sert à... regrouper les fichiers statiques. Magie !
La commande `python app/manage.py collectstatic --settings=settings_dev` fera cela pour vous.

Bien entendu, c'est une commande à répéter à chaque fois que vous faites des modifications dans les fichiers statiques.
Fastidieux ? Pas tellement : si vous utilisez le serveur de développement de Django (le truc que vous avez lancé
avec `python app/manage.py runserver`), vous n'aurez pas à vous en soucier : le serveur de développement de Django
est prévu pour aller rechercher les fichiers statiques directement dans leur répertoire d'origine.


### Les problèmes fréquents et leurs solutions connues

#### Django retourne une erreur à propos de la base de données

Pensez à créer la base de données localement si ce n'est pas encore fait,
via `python app/manage.py migrate --settings=settings_dev`

N'oubliez pas de vous créer un superuser pour accéder au site via `python app/manage.py createsuperuser --settings=settings_dev`


#### Aucune ressource statique ne semble s'afficher correctement

Les fichiers statiques doivent être collectés et placés dans le répertoire *static_pub/*.
Django peut le faire pour vous : `python app/manage.py collectstatic --settings=settings_dev`.


#### L'édito ne s'affiche pas, mais il y a une barre bleue à la place

Une partie du contenu "pratiquement statique" est géré via les *flatpages* de Django.
Il vous faudra créer ces mêmes *flatpages* si vous souhaitez avoir le même rendu (l'édito, la
page "à propos", les aides pour le balisage, etc.).


#### J'ai des erreurs 500 dès que je tente de me logguer

Vous avez créé un compte utilisateur, mais il est possible que ce compte n'ait aucun profil
associé. Dans ce cas, accédez directement à l'administration du site (adresse `/admin/`) et créez
un `Profil` que vous associez à votre compte. Cela devrait résoudre le problème.

#### Il est impossible de s'inscrire sur le site en local

L'inscription sur le site nécessite de résoudre un captcha.
Si vous utilisez les paramètres de développement, il est probable que la variable `NOCAPTCHA`
soit à `False`, signifiant que le captcha classique (celui où on entre du texte, par opposition à
celui où on ne fait que cocher une case) est actif.
Dans ce cas, il vous suffit d'écrire *PASSED* pour que le captcha soit validé.

#### Je n'arrive pas à modifier le style CSS

Ce n'est absolument pas un pré-requis pour pouvoir tester localement le site, mais si vous êtes intéressé
par la modification de la charte graphique du site, le dossier */static/css/* contient ce qu'il vous faut.
En particulier, il contient le point d'entrée Sass dans le fichier *style.scss*.
Les éléments partiels sont dans le dossier *lexpage* (ceux de Bootstrap sont, naturellement, dans le dossier *bootstrap*).
Les éléments partiels sont décomposés en plusieurs fichiers dont la sémantique est assez facile à identifier.
En particulier, le fichier *_variables.scss* contient la définition des variables (antérieures à celles de Bootstrap)
nécessaire pour le thème. Le fichier *_mixins.scss* contient des mixins nécessaires aux éléments partiels
(ou des ré-écriture de certains mixins Bootstrap, dans le cas où des modifications doivent être appliquées
directement sur ces derniers).

En environnement de développement, le fichier *app/commons/static/css/style.css* sera directement utilisé lorsque le
site est affiché (`DEBUG = True` dans les `settings`).
En environnement de production, c'est le fichier *app/static_pub/css/style.min.css* qui sera utilisé.
Notez deux choses : la première est la présence du *.min*, et la seconde est la présence du *_pub*
(voir remarque ci-dessus à propos de `collectstatic`).
