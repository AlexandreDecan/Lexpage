import os
from django.urls import reverse_lazy


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# General
SITE_ID = 1
INTERNAL_IPS = ('127.0.0.1',)
ALLOWED_HOSTS = ['127.0.0.1']
ANALYTICS = False
SITE_SCHEME = 'http'
SITE_DOMAIN = ALLOWED_HOSTS[0]
SITE_NAME = 'Roxpage'
SITE_DEMONYM = 'Roxpagiens'

# Configuration
WSGI_APPLICATION = 'wsgi.application'
ROOT_URLCONF = 'urls'
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
FIXTURE_DIRS = (os.path.join(BASE_DIR, 'fixtures'),)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.flatpages',

    'rest_framework',
    'captcha',

    'widget_tweaks',
    'commons',

    'profile.apps.Config',
    'slogan.apps.Config',
    'minichat.apps.Config',
    'blog.apps.Config',
    'messaging.apps.Config',
    'board.apps.Config',
    'notifications.apps.Config',
)

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'commons.last_visit_middleware.SetLastVisitMiddleware',
)


# Static files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_pub')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_pub')
STATIC_URL = '/static/'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
STATICFILES_STORAGE = 'minify.MinifyStatic'

MINIFY_JS = True
MINIFY_CSS = True
MINIFY_IGNORED_PATHS = ['admin/', 'images/', 'libs/jquery/src', 'rest_framework/']  # List of path prefixes

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR, 'commons', 'jinja2')],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'commons.jinja2.environment',
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'commons', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'commons.context_processors.online_settings',
                'commons.context_processors.global_settings',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.request',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Date & time
TIME_ZONE = 'Europe/Brussels'
LANGUAGE_CODE = 'fr'
USE_I18N = True
USE_L10N = True
USE_TZ = False

DATE_FORMAT = 'j F Y'
SHORT_DATE_FORMAT = 'd/m/y'
TIME_FORMAT = 'H\\hi'
DATETIME_FORMAT = DATE_FORMAT + ' ' + TIME_FORMAT
SHORT_DATETIME_FORMAT = SHORT_DATE_FORMAT + ' ' + TIME_FORMAT


# Authentification & session
AUTHENTICATION_BACKENDS = ('profile.backend.CaseInsensitiveModelBackend',)

ACCOUNT_ACTIVATION_DAYS = 5
LOGIN_REDIRECT_URL = 'homepage'
LOGIN_URL = 'auth_login'
LOGOUT_URL = 'auth_logout'

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
USER_IS_ONLINE_TIMEOUT = 5  # in minutes
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
SESSION_COOKIE_AGE = 7257600  # 3 months

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: reverse_lazy('profile_show', kwargs={'username': u.username}),
}


# Recaptcha
RECAPTCHA_PUBLIC_KEY = '6LdAH_ASAAAAACAHEysPBjLekWJX94nYM0hI3hHy'


# Themes
THEMES = {
    'ALL': (
        ('style', 'Lexpage'),
        ('style_nowel', 'Nowel'),
        ('style_st_patrick', 'Saint-Patrick'),
    ),
    'DEFAULT': 'style',
    'FORCED': None,
}
