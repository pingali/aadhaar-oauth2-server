#-*- coding: utf-8 -*-


from django.shortcuts import render_to_response
from django.template import RequestContext
from oauth2app.models import Client, AccessToken, Code
from base64 import b64encode

def client(request, client_id):
    """
    Simple function to show the codes and access tokens associated 
    with the user. This should not be used to obtain the token 
    as much as possible 
    """
    # XXX Originally this was also the callback URI for the resource
    # server. However the callback is ignored for all practical
    # purposes because the client and resource server shared the code
    # and token database.
    print "In apps.client.views.client - entered" 
    client = Client.objects.get(key=client_id)
    template = {
        "client":client,
        "basic_auth":"Basic %s" % b64encode(client.key + ":" + client.secret),
        "codes":Code.objects.filter(client=client).select_related(),
        "access_tokens":AccessToken.objects.filter(client=client).select_related()}
    template["error_description"] = request.GET.get("error_description")
    return render_to_response(
        'client/client.html', 
        template, 
        RequestContext(request))

