# Lexpage v4
Le présent dépôt contient les sources à la base de la v4 du Lexpage. Il s'agit essentiellement d'une "grosse" application Django (fragmentée en plusieurs petites applications) ainsi que les templates et les fichiers statiques nécessaires pour faire tourner le site. 

## Que contient le dépôt ?
Le répertoire */app* contient tout ce qui est propre à Django et au Lexpage : 
 - Les répertoires *blog*, *board*, *commons*, *messaging*, *minichat*, *notifications*, *profile* et *slogan* contiennent les applications. 
 - Les répertoires *media*, *media_pub*, *static*, *static_pub* contiennent les fichiers statiques. A noter que seul *static* est utilisé (*media* est bypassé pour l'upload des avatars, et les répertoires **_pub* sont présents pour que WhiteNoise accepte de servir les fichiers statiques). 
 - Le répertoire *templates* et ses sous-répertoires contiennent toutes les templates du site. Idéalement, ces templates devraient être situées dans un sous-répertoire de l'application correspondante. 
 - Les fichiers *settings.py*, *settings_base.py* et *settings_dev.py* contiennent les paramètres de Django. Par défaut, *settings.py* charge *settings_dev.py* qui lui-même charge les paramètres communs de *settings_base.py*. 
 - Le reste est classique pour du Django. 
  
La racine du dépôt contient notamment :
 - *Dockerfile* : permet de créer une image pour des containers Docker. L'image va créer un environnement Python à jour (via le fichier *requirements.txt*) et utilise Gunicorn comme serveur WSGI.
 - *gunicorn.py* contient la configuration Gunicorn à appliquer pour le site en développement.
 - *requirements.txt* contient la liste des dépendances Python nécessaires (à utiliser avec `pip install -r requirements.txt`).
 
## Comment tester localement ?
En quelques étapes :
- Cloner le dépôt via `git clone https://github.com/AlexandreDecan/Lexpage`
- Créer l'image Docker via `docker build -t lexpage:dev .`
- Créer le container via `docker run --rm -it -p 8000:80 -v PATH:/web/ lexpage:dev` où PATH est remplacé par le chemin courant
- Le site est alors accessible sur le port 8000 de votre machine.

**Mais c'est pas tout à fait pareil ?**

Et bien non, forcément, il y a de nombreuses données en production qui font que Lexpage est ce qu'il est en ligne. En particulier, certaines fonctions nécessitent un "*vrai*" SGBD, alors que l'environnement de développement travaille par défaut avec SQLite. En production, nous utilisons MariaDB que vous pourrez facilement mettre en place avec Docker. Si tel est votre souhait, pensez à ajouter *django-mysql* dans votre *requirements.txt*. 

Afin que Django ne vous crâche pas une vilaine erreur au lancement, il convient d'initialiser la base de données SQLite. Pour cela, exécutez simplement `python manage.py syncdb` (nécessite que les dépendances de `requirements.txt` soient installées, pensez donc à l'exécuter via un container, par exemple, `docker run --rm -it -v PATH:/web/ lexpage:dev python app/manage.py syncdb`)

L'édito, la page *À propos*, l'aide pour le balisage, etc. sont des *flatpages* qui sont stockées dans la base de données. Vous pouvez le faire directement depuis l'administration mais il va falloir choisir la bonne URL (indice : en fonction de vos besoins, consultez les fichiers *urls.py* !).

De même, en l'absence de contenu, certains éléments peuvent se comporter visuellement (voire comportementalement) anormalement (ce qui fait beaucoup de mots en -ment, je vous l'accorde). 


## Comment contribuer ?
De n'importe quelle manière :
- soit en me contacter pour poser vos questions ou indiquer vos remarques, 
- soit en créant une issue sur le bugtracker, 
- soit en effectuant un pull request, 
- ...
