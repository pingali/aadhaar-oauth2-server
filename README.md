Aadhaar-enabled Oauth2 Python server and client 
------------------------------------------------

Note: This is still work in progress. Contact the developer before
using it. 

The idea behind this project is to enable sharing of data (e.g.,
citizen health records in the government database) with third parties
(e.g., a private hospital) when approved by citizen. It is based on
combining oauth2, a data sharing protocol, with Aadhaar
authentication. We discuss the overall thought process in greater
detail in [Aadhaar-enabled Data Sharing v2.0](https://github.com/pingali/aadhaar-oauth2-server/raw/master/Aadhaar-enabled_Data_Sharing_2.0.pdf)

[Oauth](http://oauth.net) is an IETF-approved data-sharing
protocol. It is used by established player such as Google and Twitter
to enable easy development of third party applications with requiring
username and password. [Oauth2](http://oauth.net/2) is a more recent
and simpler version of the protocol that is in the middle of the
standardization process.

Aadhaar is a national ID project in India. It supports realtime
authentication using demographic and biometric attributes of
individuals. Please see [Aadhaar authentication API Ver 1.5 (Rev 1)][spec].

[spec]: http://uidai.gov.in/images/FrontPageUpdates/aadhaar_authentication_api_1_5_rev1_1.pdf


Intended Audience
-----------------

Developers of Aadhaar-enabled data-sharing applications. Effort has been 
made to keep the code readable but they should be able to read the code 
and experiment to get going.

Codebase 
--------

This codebase is derived from examples directory of an implementation
of Oauth2 protocol called [oauth2app][oauth2app],
[Gariel Grant's fork][oauth2app-gabriel] and Django. The code has been
extended in a few ways:

  * Separated the oauth2 client and server implementations - which were combined into one 
  * Integrated aadhaar authentication through [django-auth-aadhaar][django-auth-aadhaar]
  * Moved the logic from the front end javascript to the server 

[oauth2app]: https://github.com/hiidef/oauth2app 
[oauth2app-gabriel]: https://github.com/gabrielgrant/oauth2app 
[django-auth-aadhaar]: https://github.com/pingali/django-auth-aadhaar 

The codebase is a bit clunky and needs work to make it robust. But it
is a reasonable starting point. There are three directories: 

  * myresource: Django application that is the resource server 
  * myclient: Django application that is the client 
  * shared: Libraries and functions that are shared by both the above applications


Latest Release
--------------

  * Alpha Release (0.1) Nov 30, 2011 - Planned 
  * Platform: Linux (Ubuntu 11.04) 

Oauth2 Flow 
------------

>      Example principals: 
> 
>           Role               Example
>      Resource server      Government of India 
>      Resource client      Apollo hospital 
>      Resource owner       Resident of India
> 
>      Setup client: 
>      1. client   -----------> server [create account]
>      2. server   -----------> client [client configuration]
> 
>      Recognize owner:
>      3. owner    -----------> client [create account] 
>      
>      Request owner to authorize access: 
>      4. client   -----------> server [redirect owner to server] 
>      5. owner    -----------> server [authorize and approve data access]
>      6. server   -----------> client [access and refresh token]
>     
>      Access data and extend authorization:
>      client   -----------> server [access data for owner] 
>      client   -----------> server [refresh token] 
>      


Installation
------------

Install the dependencies first. 

>      $ sudo easy_install oauth2app
>      <Install pyAadhaarAuth from http://github.com/pingali/pyAadhaarAuth>
>      $ sudo easy_install  https://github.com/pingali/django-auth-aadhaar 

Download the source: 

>         
>      $ git clone https://github.com/pingali/aadhaar-oauth2-server 

First run the server that is the resource authorization server (say
Government of India, health department):

>      $ cd myresource
>      $ python manage.py syncdb
>      $ python manage.py runserver 127.0.0.1:8000
>      

Now visit [resource server][resource-server] (http://localhost:8000) and
signup/login. Follow instructions to create a client. The server
generates a client key or id and client secret along with information
on server configuration such as the URL for the authorization. At this
point the resource server is ready to receive an authorization request
from you.

[resource-server]: http://localhost:8000
[resource-client]: http://localhost:8001

Click on the 'download' link and store the json file attachment in the
myclient directory (as client-config.json). 

Run the client site (say private hospital). 

>      store the client configuration in myclient/client-config.json 
>      $ cd myclient
>      $ python manage.py syncdb
>      $ python manage.py runserver 127.0.0.1:8001 

Now visit the [client server][resource-client] (http://localhost:8001)
and signup/login. Create a dummy client.* When you visit the main
page, you will shown the various available resources (in this case
'last\_login', 'date\_joined' and '' (no scope or all). In each case
you will see a button asking you (user) to authorize. When you click,
you will be forwarded to the resource server (localhost:8000). At the
resource user, you will asked to login and approve or disapprove the
authorization request. Click on 'Yes' and you will be taken back to
the client site (localhost:8001). On each of your client's page, you
see a list of authorization codes. You (typically the client does it,
not the user) can now click on the authorization code and obtain a
token. The obtained token along with a refresh token is shown. You can
click on the refresh token to make the client fetch another token.

The login and approval can be both aadhaar-based or regular local
login. On the main page, if the user clicks on "Aadhaar" instead of
"Request", then the authorization will be based on aadhaar. The
resource server (http://localhost:8000) will show an aadhaar login
page instead of regular login page. The login page and authentication
is based on [django-auth-aadhaar][django-auth-aadhaar] and
[pyAadhaarAuth][pyAadhaarAuth].

Once the token is obtained, you can now query the API. Go the main 
page of the client (http://localhost:8001). At the bottom you 
will see available api paths (/api/email, /api/date_joined etc.)
and have a button for the client site and resource site. 
When you click on the resource site for any of the api calls, 
the corresponding data is accessed using the token that has 
been acquired. You should be able to see a popup with the result
of the lookup (data or error message). 

[pyAadhaarAuth]: http://github.com/pingali/pyAadhaarAuth 

*The name doesnt matter and it mostly there for legacy reasons. We
might call it an user account or whatever.

Configuration
-------------

The resource server configuration is specified in myresource/settings.py. 

       MYSITE="Resource Site"
       MYSITE_ROLE="server" 
       RESOURCE_SERVER="http://localhost:8000"
       AUTHORIZE_URL=RESOURCE_SERVER + "/oauth2/authorize"
       ACCESS_TOKEN_URL=RESOURCE_SERVER + "/oauth2/token"

       # Aadhaar-specific configuration
       AADHAAR_AUTHORIZE_URL=RESOURCE_SERVER + "/oauth2/authorize/aadhaar"
       AUTH_PROFILE_MODULE='django_auth_aadhaar.AadhaarUserProfile' 
       AADHAAR_CONFIG_FILE='fixtures/auth.cfg'
       AUTHENTICATION_BACKENDS = (     
           'django_auth_aadhaar.backend.AadhaarBackend',
           ....
  	   )


Myclient settings.py has settings that identify the role of this server
and location where the server configuration is stored. 

        MYSITE="Client Site"
        MYSITE_ROLE="client"
        CLIENT_SITE="http://localhost:8001"
        CLIENT_CONFIG='client-config.json'

The client configuration file is obtained from the server and has a
structure like this:

       { 
		 "resource_name": "Resource Site", 
		 "resource_server": "http://localhost:8000", 
		 "client_secret": "57edb78728e1e61c25cca5e104f9c5", 
		 "client_key": "d53d90894c157ab94d693a24d7a0cc"
		 "authorize_url": "http://localhost:8000/oauth2/authorize", 
		 "aadhaar_authorize_url": "http://localhost:8000/oauth2/authorize/aadhaar", 
		 "access_token_url": "http://localhost:8000/oauth2/token", 
	 }


TODO 
----

Immediate: 

  * Cleanup and logging support 
  * Apache configuration client and server

Medium term: 

  * Support for some real applications

Debugging
---------

Extensive logging is supported by the library to help with easy
application development. You may want to look at the terminal. 

Documentation
-------------

TBD 

Known Issues
------------

* Myclient uses only one client. It will not work correctly if more
  than one client are created in myclient.

Many. TBD. 

Work-in-progress    
----------------

Immediate: 

    1. Clean up the implementation including the response. Standardize
       the interface. 
    2. Test with https connection (whenever it is available) 
    3. Performance evaluation/statistics    

Medium term:  

    1. Expand the authentication support in conjunction with pyAadhaarAuth
    2. Experiment with python-oauth2 

Thanks 
------   

  * Oauth2App  - Hiidef and Gabriel Grant
  * UIDAI      - For the Aadhaar project 
  * TCS        - For support    
  * Python community - For a great development platform 
