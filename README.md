[![Build Status](https://travis-ci.org/AlexandreDecan/Lexpage.svg)](https://travis-ci.org/AlexandreDecan/Lexpage)

# Lexpage v4

Bienvenue sur le dépôt *officiel* du Lexpage ! 

Ce dépôt contient le code source de la v4 du Lexpage, tel qu'il est actuellement en production à l'adresse http://www.lexpage.net
Il s'agit essentiellement d'un ensemble de petites applications Django ainsi que des templates et les fichiers statiques
associés pour faire tourner le site. 

Certains fichiers (avatars, configuration en prod, flatpages, sniffer de la NSA, etc.) ne sont pas présents sur le dépôt pour des raisons évidentes qu'il ne faut bien entendu pas vous détailler. 

La suite de ce README s'organise ainsi : 
 - Une description rapide de ce que contient le dépôt. 
 - Des explications pour pouvoir builder et tester ce qui s'y trouve.
 - Des informations sur la manière de contribuer.
 
Bonne lecture !


## Que contient le dépôt ?
Le répertoire */app* contient tout ce qui est propre à Django et au Lexpage : 
 - Les répertoires *blog*, *board*, *commons*, *messaging*, *minichat*, *notifications*, *profile* et *slogan* contiennent les applications. 
 - Les répertoires *media*, *media_pub*, *static*, *static_pub* contiennent les fichiers statiques. *media* et *media_pub* ne sont pas utilisés. *static* contient les fichiers statiques du site, qui seront collectés automatiquement dans *static_pub* qui contiendra également les avatars uploadés.
 - Le répertoire *templates* et ses sous-répertoires contiennent toutes les templates du site. Idéalement, ces templates devraient être situées dans un sous-répertoire de l'application correspondante. 
 - Les fichiers *settings.py*, *settings_base.py* et *settings_dev.py* contiennent les paramètres de Django. Par défaut, *settings.py* charge *settings_dev.py* qui lui-même charge les paramètres communs de *settings_base.py*. 
 - Le reste est classique pour du Django. 
  
La racine du dépôt contient notamment :
 - *Dockerfile* : permet de créer une image pour des containers Docker. L'image va créer un environnement Python à jour (via le fichier *requirements.txt*) et utilise Gunicorn comme serveur WSGI.
 - *uwsgi.conf* contiet la configuration initiale pour lancer Lexpage en dev.
 - *requirements.txt* contient la liste des dépendances Python nécessaires (à utiliser avec `pip install -r requirements.txt`).
 
 
## Comment tester localement ?

Tester localement le site se fait de manière assez simple, pour peu que vous sachiez suivre une documentation :-) 

### Mettre en place un environnement virtuel

La première chose à faire, pour ne pas saloper votre environnement, c'est d'isoler le futur Lexpage. Pour cela, nous vous proposons soit d'utiliser Docker, soit d'utiliser Virtualenv/Pew. Si vous ne vous souciez pas d'installer certaines librairies dans des versions spécifiques sur votre machine de travail, vous pouvez directement passer à l'étape suivante. Bien entendu, n'importe quelle solution de virtualisation devrait vous permettre d'arriver au même résultat, mais nous ne documenterons ici que les solutions basées sur Docker et sur Virtualenv/Pew.

##### Avec Docker

Bien entendu, il est nécessaire que Docker soit installé sur votre machine. Si c'est votre première fois avec Docker, le mieux est de se rapporter à leur documentation et de suivre un bon gros tutoriel avant de vous lancer là-dedans. Enfin, rien n'est impossible, mais ça devrait vous aider.

Une image Docker est disponible via le *Dockerfile* du dépôt :
 - Créez l'image via `docker build -t lexpage/dev .` (n'oubliez pas le "." à la fin de la ligne !)
 - Créez le container via `docker run --rm -it -p 8000:8000 -v PATH:/web/ lexpage/dev` où vous remplacez *PATH* par le chemin courant. 
 - Le site est alors supporté par uWSGI et disponible sur le port 8000 de votre machine.
 
Si vous effectuez des changements dans les dépendances (autrement dit, *requirements.txt*), pensez à rebuilder l'image du container. 


##### Avec Virtualenv, Pew ou... rien !

Si vous utilisez virtualenv ou pew, créez un environnement virtuel à la racine du dépôt :
 - `pew new Lexpage -a .` si vous utilisez `pew`, 
 - `mkvirtualenv Lexpage -a .` si vous utilisez `virtualenv`.
  
Que vous soyez dans un environnement virtuel ou non, la suite est la même pour tout le monde. Installez les dépendances automatiquement avec `pip` : `pip install -r requirements.txt`

Si vous n'avez pas `pip`, ce ne sont pas les [moyens qui manquent](https://pip.pypa.io/en/latest/installing.html) tant que vous avez un Python qui tourne. 

Ensuite, par ordre de préférence : 
 - soit vous utilisez uWSGI (déjà installé) via `uwsgi --ini uwsgi.conf` 
 - soit vous utilisez le serveur de développement de Django, via `python app/manage.py runserver`

Si vous préférez *gunicorn*, rien ne vous empêche de l'utiliser également... 

### Configurer et utiliser Django pour servir Lexpage

Des paramètres de base sont proposés sur le dépôt. Les paramètres considérés comme spécifiques à l'environnement sont repris dans le fichier `settings_dev.py` qui s'occupe de charger le reste venant de `settings_base.py`. A priori, vous n'aurez pas à modifier autre chose que les paramètres de développement, mais qui sait ? Quoiqu'il en soit, si vous souhaitez utiliser un autre fichier de configuration que `settings_dev.py`, il conviendra de le signaler à Django lors de chaque appel à `python app/manage.py` (la principale commande que vous allez utiliser ici !). Faites un tour dans la documentation de Django, et vous verrez comment faire (via une variable d'environnement, ou un paramètre long, etc.). 

Avant de pouvoir tester le site, il y a quelques opérations à faire :

#### Mettre en place la base de données

Par défaut, la configuration de développement travaille avec SQLite. En production, nous tournons avec MariaDB. Si vous n'aimez pas SQLite ou que vous voulez utiliser autre chose, pensez à adapter le fichier de configuration. Dans tous les cas, si c'est la première fois que vous lancez le site, il faudra créer la base de données :
`python app/manage.py migrate`

A ce stade, une base va être créée et contiendra les différents modèles. La base est globalement vide. Des données de test sont fournies dans le répertoire `app/fixtures/`. Vous pouvez notamment charger ces données dans la base de données via : 
`python app/manage.py loaddata devel`

Si vous ne souhaitez pas utiliser ces données, mais que vous voulez tester l'authentification et ces machins-là sur le site, il vous faudra au moins un compte administrateur. Utilisez donc Django pour ça :
`python app/manage.py createsuperuser`

#### Mettre en place les fichiers statiques

Enfin, afin que le site puisse fournir les fichiers statiques nécessaires à son affichage et à son fonctionnement, il convient d'indiquer à Django de collecter ces fichiers statiques dans les différentes applications qui sont utilisées, et de les réunir dans un répertoire qui sert à fournir les fichiers statiques. La commande `python app/manage.py collectstatic` fera cela pour vous. Bien entendu, c'est une commande à répéter à chaque fois que vous faites des modifications dans les fichiers statiques. 


#### Modifier le style CSS

Ce n'est pas un pré-requis pour pouvoir tester localement le site, mais si vous êtes intéressé par la modification de la charte graphique du site, le dossier */static/css/* contient ce qu'il vous faut. En particulier, il contient le point d'entrée Sass dans le fichier *style.scss*. Les éléments partiels sont dans le dossier *lexpage* (ceux de Bootstrap sont, naturellement, dans le dossier *bootstrap*). Les éléments partiels sont décomposés en plusieurs fichiers dont la sémantique est assez facile à identifier. En particulier, le fichier *_variables.scss* contient la définition des variables (antérieures à celles de Bootstrap) nécessaire pour le thème. Le fichier *_mixins.scss* contient des mixins nécessaires aux éléments partiels (ou des ré-écriture de certains mixins Bootstrap, dans le cas où des modifications doivent être appliquées directement sur ces derniers). 

En environnement de développement, le fichier */static/css/style.css* sera directement utilisé lorsque le site est affiché. En environnement de production (ou de test), c'est le fichier */static_pub/css/style.min.css* qui sera utilisé. Notez deux choses : la première est la présence du *.min*, et la seconde est la présence du *_pub* (voir remarque ci-dessus). 

## Les problèmes fréquents et leurs solutions connues

##### mysql-python refuse de s'installer dans mon environnement virtuel

Essayez d'installer la bibliothèque de développement, par exemple, via `apt-get install libmysqlclient-dev`. Nous conseillons aussi d'avoir les bibliothèques de développement Python installées : `apt-get install python-dev`

Si cela ne convient pas, vous pouvez toujours utiliser le module `PyMySQL` plutôt que `mysql-python` en modifiant le fichier *requirements.txt*.


##### Django retourne une erreur à propos de la base de données

Pensez à créer la base de données localement si ce n'est pas encore fait, via `python app/manage.py migrate`
Si vous travaillez avec Docker, il conviendra de le faire via l'image :
`docker run --rm -it -v PATH:/web/ lexpage/dev python app/manage.py migrate` 

N'oubliez pas de vous créer un superuser pour accéder au site via `python app/manage.py createsuperuser`


##### Aucune ressource statique ne semble s'afficher correctement

Les fichiers statiques doivent être collectés et placés dans le répertoire *static_pub/*. Django peut le faire pour vous : `python app/manage.py collectstatic`.


##### L'édito ne s'affiche pas, mais il y a une barre bleue à la place

Une partie du contenu "pratiquement statique" est géré via les *flatpages* de Django. Il vous faudra créer ces mêmes *flatpages* si vous souhaitez avoir le même rendu (l'édito, la page "à propos", les aides pour le balisage, etc.). 


#### J'ai des erreurs 500 dès que je tente de me logguer

Vous avez créé un compte utilisateur, mais il est possible que ce compte n'ait aucun profil associé. Dans ce cas, accédez directement à l'administration du site (adresse `/admin/`) et créez un `Profil` que vous associez à votre compte. Cela devrait résoudre le problème. 

#### Il est impossible de s'inscrire sur le site en local

Notez qu'il n'est pas possible de s'inscrire sur le site via la procédure classique, essentiellement parce que les clés du captcha ne sont pas renseignées dans le fichier de configuration présent sur le dépôt. Si vous souhaitez créer d'autres comptes utilisateurs, il va falloir passer par l'administration de Django et faire cela à la main.


## Comment contribuer ?

De n'importe quelle manière :
  - soit en me contacter pour poser vos questions ou indiquer vos remarques, 
  - soit en créant une issue sur le bugtracker, 
  - soit en effectuant un pull request, 
  - ...

