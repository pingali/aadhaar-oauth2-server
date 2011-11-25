#-*- coding: utf-8 -*-


from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.utils.http import urlquote  as django_urlquote
from django.template import RequestContext
from uni_form.helpers import FormHelper, Submit, Reset
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from oauth2app.authorize import Authorizer, MissingRedirectURI, AuthorizationException
from oauth2app.authorize import UnvalidatedRequest, UnauthenticatedUser
from .forms import AuthorizeForm
from oauth2app.models import Client, AccessToken, Code

"""
This code is here for legacy reasons. Can be deleted. The
authorization is done by the myresource/apps/oauth2 
"""
@login_required
def missing_redirect_uri(request):
    return render_to_response(
        'oauth2/missing_redirect_uri.html', 
        {}, 
        RequestContext(request))


@login_required
def authorize(request, aadhaar=False):
    
    raise Exception("Client authorize. Should not come here") 

    print "Came here - authorizer aadhaar = ", aadhaar
    authorizer = Authorizer()
    try:
        # Check if the correct user is logged in. Else redirect to login
        # page 
        loggedin_user = request.user 
        print "logged in user = ", loggedin_user 
        client_id = request.REQUEST.get('client_id') 
        client =  Client.objects.get(key=client_id)
        if client == None: 
            raise AuthorizationException("Unknown client") 
        
        # This is necessary if the logged in user is different from
        # the client identified. This is possibly a legacy issue. The 
        # check is useful anyway. 
        resource_owner = client.user 
        print "resource owner = ", resource_owner 
        if (loggedin_user != resource_owner):
            auth.logout(request)
            next=django_urlquote(request.get_full_path())
            if aadhaar: 
                nexturl = ("/account/aadhaar/authenticate/?next=%s" % next)
            else:
                nexturl = ("/account/login/?next=%s" % next)
            print "sending the user to ", nexturl 
            return HttpResponseRedirect(nexturl)
        
        # Now authorize
        authorizer.validate(request)

    except MissingRedirectURI, e:
        return HttpResponseRedirect("/oauth2/missing_redirect_uri")
    except AuthorizationException, e:
        # The request is malformed or invalid. Automatically 
        # redirects to the provided redirect URL.
        return authorizer.error_redirect()
    if request.method == 'GET':
        # Make sure the authorizer has validated before requesting the client
        # or access_ranges as otherwise they will be None.
        template = {
            "client":authorizer.client, 
            "access_ranges":authorizer.access_ranges}
        template["form"] = AuthorizeForm()
        helper = FormHelper()
        no_submit = Submit('connect','No')
        helper.add_input(no_submit)
        yes_submit = Submit('connect', 'Yes')
        helper.add_input(yes_submit)
        helper.form_action = '/oauth2/authorize?%s' % authorizer.query_string
        helper.form_method = 'POST'
        template["helper"] = helper
        return render_to_response(
            'oauth2/authorize.html', 
            template, 
            RequestContext(request))
    elif request.method == 'POST':
        form = AuthorizeForm(request.POST)
        if form.is_valid():
            if request.POST.get("connect") == "Yes":
                return authorizer.grant_redirect()
            else:
                return authorizer.error_redirect()
    return HttpResponseRedirect("/")
