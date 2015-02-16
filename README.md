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


### Avec Docker

Une image Docker est disponible via le *Dockerfile* du dépôt :
 - Créez l'image via `docker build -t lexpage:dev .`
 - Créez le container via `docker run --rm -it -p 8000:8000 -v PATH:/web/ lexpage:dev` où vous remplacez *PATH* par le chemin courant. 
 - Le site est alors supporté par uWSGI et disponible sur le port 8000 de votre machine.
 
Si vous effectuez des changements dans les dépendances (autrement dit, *requirements.txt*), pensez à rebuilder l'image du container. 

### Avec Virtualenv, Pew ou... rien !

Si vous utilisez virtualenv ou pew, créez un environnement virtuel à la racine du dépôt. Puis, quelque soit votre choix, faites
`pip install -r requirements.txt`

Ensuite :
 - soit vous utilisez le serveur de développement de Django, via `python app/manage.py runserver`
 - soit vous utilisez Gunicorn (à installer via `pip install gunicorn`) via `gunicorn --config gunicorn.conf wsgi:application`
 - soit vous utilisez uWSGI (déjà installé) via `uwsgi --ini uwsgi.conf`

Dans tous les cas, n'oubliez pas que Django nécessite que les fichiers statiques soient collectés dans le répertoire *static_pub*. Cela peut être fait automatiquement :
`python app/manage.py collecstatic`
 

## Les problèmes fréquents et leurs solutions connues

*mysql-python refuse de s'installer dans mon environnement virtuel*

Essayez d'installer la librairie de développement, par exemple, via `apt-get install libmysqlclient-dev`

*Django retourne une erreur à propos de la base de données*

Pensez à créer la base de données localement si ce n'est pas encore fait, via `python manage.py syncdb` ou encore via `python manage.py migrate` (Django 1.7+).
Si vous travaillez avec Docker, il conviendra de le faire via l'image :
`docker run --rm -it -v PATH:/web/ lexpage:dev python app/manage.py syncdb` 

*Aucune ressource statique ne semble s'afficher correctement*

Vous n'avez pas oublié `python manage.py collecstatic` ?

*L'édito ne s'affiche pas, mais il y a une barre bleue à la place*

Une partie du contenu "pratiquement statique" est géré via les *flatpages* de Django. Il vous faudra créer ces mêmes *flatpages* si vous souhaitez avoir le même rendu (l'édito, la page "à propos", les aides pour le balisage, etc.). 



## Comment contribuer ?
De n'importe quelle manière :
  - soit en me contacter pour poser vos questions ou indiquer vos remarques, 
  - soit en créant une issue sur le bugtracker, 
  - soit en effectuant un pull request, 
  - ...
  
