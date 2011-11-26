# Django settings for oauth2app example myclient project.

import os, sys
here = lambda path: os.path.abspath(os.path.join(os.path.dirname(__file__),path))
import simplejson as json 

if os.name == "posix":
    sep = "/"
else:
    sep = "\\"

sys.path.insert(0, here(".."))
sys.path.insert(0, here("..%s.." % sep))
sys.path.insert(0, here("..%s..%sdjango-auth-aadhaar" % (sep,sep)))
sys.path.insert(0, here("..%s..%soauth2app-aadhaar" % (sep,sep)))
import oauth2app 

MYSITE="Client Site"
MYSITE_ROLE="client"
CLIENT_SITE="http://localhost:8001"
CLIENT_CONFIG=here('client-config.json')

if (os.path.isfile(CLIENT_CONFIG)):
    conf = json.loads(file(CLIENT_CONFIG).read())

    RESOURCE_CLIENT_KEY    = conf['client_key']
    RESOURCE_CLIENT_SECRET = conf['client_secret']
    RESOURCE_NAME          = conf['resource_name']
    RESOURCE_SERVER        = conf['resource_server']
    AUTHORIZE_URL          = conf['authorize_url']
    AADHAAR_AUTHORIZE_URL  = conf['aadhaar_authorize_url']
    ACCESS_TOKEN_URL       = conf['access_token_url']

else: 
    RESOURCE_CLIENT_KEY="0ede34172e5fddac57be3205e01140"
    RESOURCE_CLIENT_SECRET="6f62e649762b27ce8f788d65a922ef"
    RESOURCE_SERVER="http://localhost:8000"
    AUTHORIZE_URL=RESOURCE_SERVER + "/oauth2/authorize"
    AADHAAR_AUTHORIZE_URL=RESOURCE_SERVER + "/oauth2/authorize/aadhaar"
    ACCESS_TOKEN_URL=RESOURCE_SERVER + "/oauth2/token"

# To ensure that myresource and myclient sessions dont client 
# in case they are run on the same machine 
SESSION_COOKIE_NAME="clientsite"
CSRF_COOKIE_NAME="clientcsrf" 

DEBUG = True
TEMPLATE_DEBUG = DEBUG

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
   here('apps/account/fixtures'),
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

STATICFILES_DIRS = (here('static'),)

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
    here('templates'),
    here('..%sshared%stemplates' % (sep, sep)),
    )

AUTH_PROFILE_MODULE='django_auth_aadhaar.AadhaarUserProfile' 
AADHAAR_CONFIG_FILE=here('fixtures/auth.cfg')
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
    'myclient.apps.client',
    'shared.apps.account',
    'myclient.apps.oauth2',
    'myclient.apps.api',
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

