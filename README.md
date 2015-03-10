# Lexpage v4
Le présent dépôt contient les sources à la base de la v4 du Lexpage. Il s'agit essentiellement d'une "grosse" application Django (fragmentée en plusieurs petites applications) ainsi que les templates et les fichiers statiques nécessaires pour faire tourner le site. 


## Que contient le dépôt ?
Le répertoire */app* contient tout ce qui est propre à Django et au Lexpage : 
 - Les répertoires *blog*, *board*, *commons*, *messaging*, *minichat*, *notifications*, *profile* et *slogan* contiennent les applications. 
 - Les répertoires *media*, *media_pub*, *static*, *static_pub* contiennent les fichiers statiques. *media* et *media_pub* ne sont pas utilisés. *static* contient les fichiers statiques du site, qui seront collectés automatiquement dans *static_pub* qui contiendra également les avatars uploadés.
 - Le répertoire *templates* et ses sous-répertoires contiennent toutes les templates du site. Idéalement, ces templates devraient être situées dans un sous-répertoire de l'application correspondante. 
 - Les fichiers *settings.py*, *settings_base.py* et *settings_dev.py* contiennent les paramètres de Django. Par défaut, *settings.py* charge *settings_dev.py* qui lui-même charge les paramètres communs de *settings_base.py*. 
 - Le reste est classique pour du Django. 
  
La racine du dépôt contient notamment :
 - *Dockerfile* : permet de créer une image pour des containers Docker. L'image va créer un environnement Python à jour (via le fichier *requirements.txt*) et utilise Gunicorn comme serveur WSGI.
 - *gunicorn.conf* et *uwsgi.conf* contiennent des configurations initiales pour lancer Lexpage en dev.
 - *requirements.txt* contient la liste des dépendances Python nécessaires (à utiliser avec `pip install -r requirements.txt`).
 
 
## Comment tester localement ?

Pour ne pas saloper votre environnement, nous vous conseillons d'utiliser Docker, virtualenv ou encore pew. 


##### Avec Docker

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
 - soit vous utilisez Gunicorn (à installer via `pip install gunicorn`) via `gunicorn --config gunicorn.conf wsgi:application`
 - soit vous utilisez le serveur de développement de Django, via `python app/manage.py runserver`

#### Dans tous les cas...

N'oubliez pas que vous n'avez probablement pas, à ce stade, de base de données prêtes. Il convient d'utiliser `python app/manage.py migrate` pour créer la base de données (localement, par défaut, avec SQLite). Afin de pouvoir tester le site, il est pratique d'avoir un compte superuser : `python app/manage.py createsuperuser` qui va vous demander d'entrer quelques informations. A l'aide de ce compte utilisateur, vous pourrez par la suite créer d'autres utilisateurs via l'administration de Django (accessible dans un menu du site). 

Enfin, afin que le site puisse fournir les fichiers statiques nécessaires à son affichage et à son fonctionnement, il convient d'indiquer à Django de collecter ces fichiers statiques dans les différentes applications qui sont utilisées, et de les réunir dans un répertoire qui sert à fournir les fichiers statiques. La commande `python app/manage.py collectstatic` fera cela pour vous. Bien entendu, c'est une commande à répéter à chaque fois que vous faites des modifications dans les fichiers statiques. 

## Les problèmes fréquents et leurs solutions connues

##### mysql-python refuse de s'installer dans mon environnement virtuel

Essayez d'installer la bibliothèque de développement, par exemple, via `apt-get install libmysqlclient-dev`. 
Si cela ne convient pas, vous pouvez toujours utiliser le module `PyMySQL` plutôt que `mysql-python` en modifiant le fichier *requirements.txt*.

##### Django retourne une erreur à propos de la base de données

Pensez à créer la base de données localement si ce n'est pas encore fait, via `python app/manage.py migrate`
Si vous travaillez avec Docker, il conviendra de le faire via l'image :
`docker run --rm -it -v PATH:/web/ lexpage/dev python app/manage.py migrate` 

N'oubliez pas de vous créer un superuser pour accéder au site via `python app/manage.py createsuperuser`

##### Aucune ressource statique ne semble s'afficher correctement

Les fichiers statiques doivent être collectés et placés dans le répertoire *static_pub/*. Django peut le faire pour vous : `python app/manage.py collecstatic` ?

##### L'édito ne s'affiche pas, mais il y a une barre bleue à la place

Une partie du contenu "pratiquement statique" est géré via les *flatpages* de Django. Il vous faudra créer ces mêmes *flatpages* si vous souhaitez avoir le même rendu (l'édito, la page "à propos", les aides pour le balisage, etc.). 

#### J'ai des erreurs 500 dès que je tente de me logguer

Vous avez créé un compte utilisateur, mais il est possible que ce compte n'ait aucun profil associé. Dans ce cas, accédez directement à l'administration du site (adresse `/admin/`) et créez un `Profil` que vous associez à votre compte. Cela devrait résoudre le problème. 

#### Il est impossible de s'inscrire sur le site en local

Notez qu'il n'est pas possible de s'inscrire sur le site via la procédure classique, essentiellement parce que les clés du captcha ne sont pas renseignées dans le fichier de `settings` présent sur le dépôt. Si vous souhaitez créer d'autres comptes utilisateurs, il va falloir passer par l'administration de Django et faire cela à la main.


## Comment contribuer ?
De n'importe quelle manière :
  - soit en me contacter pour poser vos questions ou indiquer vos remarques, 
  - soit en créant une issue sur le bugtracker, 
  - soit en effectuant un pull request, 
  - ...
  
