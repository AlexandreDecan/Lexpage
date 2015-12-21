from settings_base import *


SECRET_KEY = 'SecretKeyForDevelopmentEnvironment'

RECAPTCHA_PRIVATE_KEY = None
# Set NOCAPTCHA to True to have a checkbox as captcha.
# Set NOCAPTCHA to False to have an input field.
# Enter "PASSED" in this field to bypass captcha while testing.
NOCAPTCHA = False
os.environ['RECAPTCHA_TESTING'] = 'True'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'no-reply@lexpage.net'

ADMINS = (
    ('AdminDev', 'admin.dev@fakemail.com'),
)
MANAGERS = ADMINS

DEBUG = True
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ('127.0.0.1',)
ALLOWED_HOSTS = ['127.0.0.1',]

LOGGING = None

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db'),
    }
}
