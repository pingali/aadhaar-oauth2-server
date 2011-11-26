Directory Structure
-------------------

* myresource: Serve authorization and access requests from the client 
     * apps/base: Home page for the user showing all the clients, tokens
     * apps/client: Shows a given client all the codes and tokens
       associated with the client. Effectively duplicates the base
       code.
     * apps/account: Account creation, downloading the client
       configuration, and aadhaar-based authentication
     * apps/oauth2: Show the authorize page once authenticated by
       the apps/account code.
     * fixtures: configuration information for aadhaar authentication 