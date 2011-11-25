Oauth2 python server and client Aadhaar Authentication Service 
---------------------------------------------------------------

Note: This is still work in progress. Contact the developer before
using it. 

The idea behind this project is to enable sharing of data (e.g.,
citizen health records in the government database) with third parties
(e.g., a private hospital) when approved by citizen. It is based on
combining oauth2, a data sharing protocol, with Aadhaar
authentication. 

Oauth2 is a IETF-approved data-sharing protocol. It is used by
established player such as Google and Twitter. Oauth2 is a more recent
and simpler version of the protocol that is in the middle of the
standardization process. 

Aadhaar is a national ID project in India. It supports realtime
authentication using demographic and biometric attributes of
individuals. Please see [Aadhaar authentication API Ver 1.5 (Rev 1)][spec].

[spec]: http://uidai.gov.in/images/FrontPageUpdates/aadhaar_authentication_api_1_5_rev1_1.pdf


Intended audience
-----------------

Developers of Aadhaar-based application developers. Effort has been
made to keep the code readable but they should be able to read the
code and experiment to get going. 

Codebase
--------

This codebase is derived from examples directory of an implementation
of Oauth2 protocol called [oauth2app][oauth2app] and Django. The code
has been expanded in a few ways:

   1. Separated the oauth2 client and server implementations - which were combined into one 
   2. Integrated aadhaar authentication through [django-auth-aadhaar][django-auth-aadhaar]
   3. Moved the logic from the front end javascript to the server 

[oauth2app]: https://github.com/hiidef/oauth2app 
[django-auth-aadhaar]: https://github.com/pingali/django-auth-aadhaar

The codebase is a bit clunky and needs work to make it robust. But it
is a reasonable starting point. 

Latest Release
--------------

  * Alpha Release (0.1) Nov 30, 2011 - Planned 
  * Supported platform: Linux (Ubuntu) 

Oauth2 Flow 
------------

>      Example principals: 
> 
>               Role            Example
>          Resource server      Government of India 
>          Resource client      Apollo hospital 
>          Resource owner       Resident of India
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


>      $ sudo easy_install oauth2app
>      <install pyAadhaarAuth from https://github.com/pingali/pyAadhaarAuth> 
>      $ sudo easy_install  https://github.com/pingali/django-auth-aadhaar 

Download the source: 

>         
>      $ git clone https://github.com/pingali/aadhaar-oauth2-server 

First run the server that is the resource authorization server (say
Government of India, health department):

>      $ cd myresource
>      $ python manage.py syncdb
>      $ python manage.py runserver 127.0.0.1:8000
>      Create user and download client configuration as suggested below 

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

[pyAadhaarAuth]: http://github.com/pingali/pyAadhaarAuth 

*The name doesnt matter and it mostly there for legacy reasons. We
might call it an user account or whatever.

Debugging
---------

Extensive logging is supported by the library to help with easy
application development. You may want to look at the terminal. 

Documentation
-------------

TBD 

Known Issues
------------

Many. TBD. 

Work-in-progress    
----------------

  Immediate: 

    1. Clean up the implementation
    2. Test with https connection (whenever it is available) 
    3. Performance evaluation/statistics    

  Medium term:  

    1. Expand the authentication support 

Thanks 
------   

  * Oauth2App  - Hiidef and Gabriel Grant
  * UIDAI      - For the Aadhaar project 
  * TCS        - For support    
  * Python community - For a great development platform 
