import os
from django.core.urlresolvers import reverse_lazy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# General
SITE_ID = 1
INTERNAL_IPS = ('127.0.0.1',)
ALLOWED_HOSTS = ['www.lexpage.net', '127.0.0.1']
ANALYTICS = False  # Overridden in prod

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
    'captcha',
    'ws4redis',

    'profile',
    'slogan',
    'widget_tweaks',
    'commons',
    'minichat',
    'blog',
    'messaging',
    'board',
    'notifications',

)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'profile.last_visit_middleware.SetLastVisitMiddleware',
)


# Static files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_pub')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_pub')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# Templates
TEMPLATES = [  # https://docs.djangoproject.com/en/1.9/ref/templates/upgrading/#the-templates-settings
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'context_processors.global_settings',
                'ws4redis.context_processors.default',
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

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
USER_IS_ONLINE_TIMEOUT = 5
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
SESSION_COOKIE_AGE = 7257600  # 3 months

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: reverse_lazy('profile_show', kwargs={'username': u.username}),
}


# Websockets
WEBSOCKET_URL = '/ws/'
WS4REDIS_HEARTBEAT = '--w4s--'
from websockets_helpers import get_allowed_channels
WS4REDIS_ALLOWED_CHANNELS = get_allowed_channels


# Recaptcha
RECAPTCHA_PUBLIC_KEY = '6LdAH_ASAAAAACAHEysPBjLekWJX94nYM0hI3hHy'

# Themes
THEMES = {
    'ALL': (
        ('style', 'Lexpage'),
        ('style_nowel', 'Nowel'),
    ),
    'DEFAULT': 'style'
}

