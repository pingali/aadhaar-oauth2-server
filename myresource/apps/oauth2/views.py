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

@login_required
def missing_redirect_uri(request):
    return render_to_response(
        'oauth2/missing_redirect_uri.html', 
        {}, 
        RequestContext(request))


@login_required
def authorize(request):
    print "Came here - authorizer"
    authorizer = Authorizer()
    try:
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

def aadhaar_login_required(f):
    print "aadhaar login decorator"
    def wrap(request, *args, **kwargs):
        redirect=False
        user = request.user 
        if not user.is_authenticated(): 
            print "aadhaar login decorator: User not found"
            redirect = True 
        else: 
            print "aadhaar login decorator: Found user ", user 
            profile = user.get_profile() 
            if not profile.is_valid_aadhaar(): 
                print "Not an aadhaar login. So redirect"
                redirect = True 
            else:
                print "aadhaar login decorator: valid aadhaar profile", profile
        if (redirect): 
            print "Logging out and redirecting"
            auth.logout(request)
            next=django_urlquote(request.get_full_path())
            nexturl = ("/account/aadhaar/authenticate/?next=%s" % next)
            print "sending the user to ", nexturl 
            return HttpResponseRedirect(nexturl)
        else:
            print "All is well. So process"
            return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

@aadhaar_login_required
def authorize_aadhaar(request):
    print "Came here - authorizer "
    authorizer = Authorizer()
    try:
        loggedin_user = request.user 
        client_id = request.REQUEST.get('client_id') 
        client =  Client.objects.get(key=client_id)
        if client == None: 
            raise AuthorizationException("Unknown client") 
        
        print "Authorizing the request" 
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
        helper.form_action = '/oauth2/authorize/aadhaar?%s' % authorizer.query_string
        helper.form_method = 'POST'
        template["helper"] = helper
        return render_to_response(
            'oauth2/authorize.html', 
            template, 
            RequestContext(request))
    elif request.method == 'POST':
        form = AuthorizeForm(request.POST)
        if form.is_valid():
            auth.logout(request)
            if request.POST.get("connect") == "Yes":
                redirect = authorizer.grant_redirect()
            else:
                redirect = authorizer.error_redirect()
            auth.logout(request)
            return redirect
    # Dont let the user do any other add/deletes etc.
    auth.logout(request)
    return HttpResponseRedirect("/")
