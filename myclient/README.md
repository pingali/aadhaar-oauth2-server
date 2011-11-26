Directory Structure
-------------------

* myclient: Interface with the enduser 
     * apps/base: Home page for the user showing all the clients, tokens
     * apps/account: Handle the signup from the user 
     * apps/client: Main module that handle obtaining the codes and tokens 
     * apps/oauth2: This is not used by the client. It is only used
           by the server.
     * fixtures: configuration information for aadhaar authentication  
       (used only by the resource server at this moment) 