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

### Docker

Une image Docker est disponible via le *Dockerfile* du dépôt :
 - Créez l'image via `docker build -t lexpage:dev .`
 - Créez le container via `docker run --rm -it -p 8000:8000 -v PATH:/web/ lexpage:dev` où vous remplacez *PATH* par le chemin courant. 
 - Le site est alors supporté par uWSGI et disponible sur le port 8000 de votre machine.
 
Si vous effectuez des changements dans les dépendances (autrement dit, *requirements.txt*), pensez à rebuilder l'image du container. 

### Rien, Virtualenv ou Pew

Si vous utilisez virtualenv ou pew, créez un environnement virtuel à la racine du dépôt. Puis, quelque soit votre choix, faites
`pip install -r requirements.txt`

Ensuite :
 - soit vous utilisez le serveur de développement de Django, via `python app/manage.py runserver`
 - soit vous utilisez Gunicorn (à installer via `pip install gunicorn`) via `gunicorn --config gunicorn.conf wsgi:application`
 - soit vous utilisez uWSGI (déjà installé) via `uwsgi --ini uwsgi.conf`

Dans tous les cas, n'oubliez pas que Django nécessite que les fichiers statiques soient collectés dans le répertoire *static_pub*. Cela peut être fait automatiquement :
`python app/manage.py collecstatic`
 

**Mais c'est pas tout à fait pareil ?**

Et bien non, forcément, il y a de nombreuses données en production qui font que Lexpage est ce qu'il est en ligne. En particulier, certaines fonctions nécessitent un "*vrai*" SGBD, alors que l'environnement de développement travaille par défaut avec SQLite. En production, nous utilisons MariaDB que vous pourrez facilement mettre en place avec Docker. 

1) Afin que Django ne vous crâche pas une vilaine erreur au lancement, il convient d'initialiser la base de données SQLite. Pour cela, exécutez simplement `python manage.py syncdb` (nécessite que les dépendances de `requirements.txt` soient installées, pensez donc à exécuter `docker run --rm -it -v PATH:/web/ lexpage:dev python app/manage.py syncdb` si vous travaillez avec le container Docker)

2) L'édito, la page "à propos", l'aide pour le balisage, etc. sont des *flatpages* qui sont stockées dans la base de données. Vous pouvez le faire directement depuis l'administration mais il va falloir choisir la bonne URL pour chaque flatpage (indice : en fonction de vos besoins, consultez le fichier *urls.py* à la racine, ou la template *navbar.html*, par exemple).

3) De même, en l'absence de contenu, certains éléments peuvent se comporter visuellement (voire comportementalement) anormalement (ce qui fait beaucoup de mots en -ment, je vous l'accorde). 

4) Au fait, vous n'avez pas oublié de faire un `python manage.py collectstatic` ?


## Comment contribuer ?
De n'importe quelle manière :
- soit en me contacter pour poser vos questions ou indiquer vos remarques, 
- soit en créant une issue sur le bugtracker, 
- soit en effectuant un pull request, 
- ...
