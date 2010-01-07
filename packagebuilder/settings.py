# Django settings for packagebuilder project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Ryan Shaw', 'ryanshaw@ischool.berkeley.edu'),
)

MANAGERS = ADMINS

TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

# Number of days users have to activate their accounts after registering.
ACCOUNT_ACTIVATION_DAYS = 7

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

# TEMPLATE_CONTEXT_PROCESSORS = (
#     'django.core.context_processors.auth',
#     'django.core.context_processors.debug',
#     'django.core.context_processors.i18n',
#     'django.core.context_processors.media',
#     'django_authopenid.context_processors.authopenid',
# )

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django_authopenid.middleware.OpenIDMiddleware',
)

ROOT_URLCONF = 'packagebuilder.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'registration',
    #'django_authopenid',
    'packagebuilder.main'
)

from settings_local import *
