# Django settings for oauth2app example myresource project.

import os, sys

def findpath(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__),path))

DEVELOPMENT=True 
DEBUG = True
TEMPLATE_DEBUG = DEBUG

sys.path.insert(0, findpath(".."))
if DEVELOPMENT: 
    if os.name == "posix":
        sep = "/"
    else:
        sep = "\\"
        
    sys.path.insert(0, findpath("..%s.." % sep))
    sys.path.insert(0, findpath("..%s..%sdjango-auth-aadhaar" % (sep,sep)))
    sys.path.insert(0, findpath("..%s..%soauth2app-aadhaar" % (sep,sep)))


ADMINS = ()
MANAGERS = ADMINS

#
# => Configuration this server end
# 
MYSITE="Resource Site"
MYSITE_ROLE="server" 
RESOURCE_SERVER="http://localhost:8000"
AUTHORIZE_URL=RESOURCE_SERVER + "/oauth2/authorize"
AADHAAR_AUTHORIZE_URL=RESOURCE_SERVER + "/oauth2/authorize/aadhaar"
ACCESS_TOKEN_URL=RESOURCE_SERVER + "/oauth2/token"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': 'myresource.sqlite.db',      
        'USER': '',      
        'PASSWORD': '',  
        'HOST': '',      
        'PORT': '',      
    }
}

FIXTURE_DIRS = (
   findpath('apps/account/fixtures'),
)

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
LOGIN_URL = "/account/login"
MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = ''
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/static/admin/'
STATICFILES_DIRS = (findpath('static'),)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = '=hf03e+08xlolbb$!-s01m-n_4xn*5mdsd!pm@$+ms!pe08f-7'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'shared.context_processors.myresource_context'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'shared.xsmiddleware.XsSharing',
)

ROOT_URLCONF = 'myresource.urls'

TEMPLATE_DIRS = (
    findpath('templates'),
    findpath('..%sshared%stemplates' % (sep, sep)),
    )

# Configure the aadhaar-based authentication 
AUTH_PROFILE_MODULE='django_auth_aadhaar.AadhaarUserProfile' 
AADHAAR_CONFIG_FILE=findpath('fixtures/auth.cfg')
AUTHENTICATION_BACKENDS = (     
    'django_auth_aadhaar.backend.AadhaarBackend',
    #'django.contrib.auth.backends.RemoteUserBackend',
    'django.contrib.auth.backends.ModelBackend',
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shared',
    'shared.apps.base',
    'myresource.apps.client',
    'myresource.apps.account',
    'myresource.apps.oauth2',
    'myresource.apps.api',
    'uni_form',
    'oauth2app',
    'django_auth_aadhaar')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

