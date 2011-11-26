# Django settings for oauth2app example myclient project.

import os, sys
import simplejson as json 
import logging 


def findpath(path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__),path))

DEVELOPMENT=True 
DEBUG = True
TEMPLATE_DEBUG = DEBUG


# For shared 
sys.path.insert(0, findpath(".."))

if DEVELOPMENT: 
    if os.name == "posix":
        sep = "/"
    else:
        sep = "\\"
    sys.path.insert(0, findpath("..%s.." % sep))
    sys.path.insert(0, findpath("..%s..%sdjango-auth-aadhaar" % (sep,sep)))
    sys.path.insert(0, findpath("..%s..%soauth2app-aadhaar" % (sep,sep)))

#
# => Configure the client server and load the client config file
# 
MYSITE="Client Site"
MYSITE_ROLE="client"
CLIENT_SITE="http://localhost:8001"
CLIENT_CONFIG=findpath('client-config.json')

if (not os.path.isfile(CLIENT_CONFIG)):
    raise Exception("Missing client configuration file") 

# => Load configuration 
conf = json.loads(file(CLIENT_CONFIG).read())
RESOURCE_CLIENT_KEY    = conf['client_key']
RESOURCE_CLIENT_SECRET = conf['client_secret']
RESOURCE_NAME          = conf['resource_name']
RESOURCE_SERVER        = conf['resource_server']
AUTHORIZE_URL          = conf['authorize_url']
AADHAAR_AUTHORIZE_URL  = conf['aadhaar_authorize_url']
ACCESS_TOKEN_URL       = conf['access_token_url']

# To ensure that myresource and myclient sessions dont client 
# in case they are run on the same machine 
SESSION_COOKIE_NAME="clientsite"
CSRF_COOKIE_NAME="clientcsrf" 

ADMINS = ()
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': 'myclient.sqlite.db',      
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

SECRET_KEY = '=hff1e+08xoolbb$!-s01m-n_4xn*5mdsd!pm@$+ms!pe08f-7'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
    'django.template.loaders.app_directories.load_template_source',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'shared.context_processors.myclient_context',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'shared.xsmiddleware.XsSharing',
)

ROOT_URLCONF = 'myclient.urls'

TEMPLATE_DIRS = (
    findpath('templates'),
    findpath('..%sshared%stemplates' % (sep, sep)),
    )

# => Not user by client but is supported just in case 
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
    'shared.apps.account',
    'myclient.apps.client',
    'myclient.apps.oauth2',
    'myclient.apps.api',
    'uni_form',
    'oauth2app',
    'django_auth_aadhaar')


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-6s: %(name)s - %(levelname)s - %(message)s',
                    #filename=findpath('django.log'),
                    #filemode='a+',
                    )

#
#LOGGING = {
#    'version': 1,
#    'disable_existing_loggers': True,
#    'formatters': {
#        'verbose': {
#            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
#        },
#        'simple': {
#            'format': '%(levelname)s %(message)s'
#        },
#    },
#    'filters': {
#    },
#    'handlers': {
#        'null': {
#            'level':'DEBUG',
#            'class':'django.utils.log.NullHandler',
#        },
#        'console':{
#            'level':'DEBUG',
#            'class':'logging.StreamHandler',
#            'formatter': 'simple'
#        },
#        'mail_admins': {
#            'level': 'ERROR',
#            'class': 'django.utils.log.AdminEmailHandler',
#            'filters': []
#        }
#    },
#    'loggers': {
#        'django': {
#            'handlers':['console'],
#            'propagate': True,
#            'level':'DEBUG',
#        },
#        'django.request': {
#            'handlers': ['mail_admins'],
#            'level': 'ERROR',
#            'propagate': False,
#        },
#    }
#}
#
