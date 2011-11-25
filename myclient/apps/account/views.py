#-*- coding: utf-8 -*-


from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from oauth2app.models import Client, AccessRange
from .forms import SignupForm, LoginForm, CreateClientForm, ClientRemoveForm, AadhaarLoginForm

@login_required
def clients(request):
    if request.method == "POST":
        form = CreateClientForm(request.POST)
        remove_form = ClientRemoveForm(request.POST)
        if form.is_valid():
            Client.objects.create(
                name=form.cleaned_data["name"],
                user=request.user)
        elif remove_form.is_valid():
            Client.objects.filter(
                id=remove_form.cleaned_data["client_id"]).delete()
            form = CreateClientForm()           
    else:
        form = CreateClientForm()

    template = {
        "form":form, 
        "clients":Client.objects.filter(user=request.user)}
    return render_to_response(
        'account/clients.html', 
        template, 
        RequestContext(request))    


def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password"])
            auth.login(request, user)
            if request.POST.get('next'):
                next = form.cleaned_data['next'] 
            else:
                next = "/"
            print "[POST] redirecting from login page to ", next 
            return HttpResponseRedirect(next) 

    else:
        # Support redirect
        initial = {} 
        if request.GET.get('next') != None: 
            next = request.GET.get('next')
            initial['next'] = next 
            print "[GET] redirecting from login page to ", next 
        form = LoginForm(initial=initial)

    template = {"form":form}
    return render_to_response(
        'account/login.html', 
        template, 
        RequestContext(request))
 
    
@login_required    
def logout(request):
    auth.logout(request)
    return render_to_response(
        'account/logout.html', 
        {}, 
        RequestContext(request))


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                    form.cleaned_data["username"],
                    form.cleaned_data["email"],
                    form.cleaned_data["password1"],)
            user = auth.authenticate(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password1"])
            auth.login(request, user)
            return HttpResponseRedirect("/")
    else:
        form = SignupForm()
    template = {"form":form}
    return render_to_response(
        'account/signup.html', 
        template, 
        RequestContext(request))

def aadhaar_login(request):

    if request.method == "POST":
        print "received post", request.POST 
        form = AadhaarLoginForm(request.POST)
        print form 
        if form.is_valid():
            credentials = form.cleaned_data 
            # cleanup and extract the aadhaar 
            auth_params = {} 
            for k,v in credentials.iteritems():
                if k.startswith('aadhaar'):
                    auth_params[k] = v
            print auth_params 
            user = auth.authenticate(**auth_params) 
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    state = "You're successfully logged in!"
                    if request.POST.get('next'):
                        next = form.cleaned_data['next'] 
                    else:
                        next = "/"
                    return HttpResponseRedirect(next) 
                else:
                    state = "Your account is not active, please contact the site admin."
        else:
            state = "You could not be authenticated" 

    else:
        # Support redirect
        initial = {} 
        if request.GET.get('next') != None: 
            next = request.GET.get('next')
        else:
            next = "/"
        initial['next'] = next 
        form = AadhaarLoginForm(initial=initial)
            
    template = {"form":form}
    return render_to_response(
        'account/aadhaar_login.html', 
        template, 
        RequestContext(request))
 
