from __future__ import unicode_literals 
 
from django.shortcuts import render, HttpResponse, redirect 
from django.utils.html import escape
from django.contrib import messages
from .models import User

class Route(object):
    REDIRECT_ROUTE = '/travels/'

def login(request):
    if 'user_session' in request.session and request.session['user_session']:
        return redirect(Route.REDIRECT_ROUTE)
    else:
        return render(request, "users_app/index.html") 

def register(request):
    if 'user_session' in request.session and request.session['user_session']:
        return redirect(Route.REDIRECT_ROUTE)
    else:
        return render(request, "users_app/register.html")

def verify_login(request):
    response = User.objects.login_validator(request.POST)
    goto = Route.REDIRECT_ROUTE

    if response['status']:
        request.session['user_session']=response['user'].id

        clearSessions(request.session)
    else:
        request.session['username'] = request.POST['username']
        
        for tag, error in response['errors'].iteritems():
            messages.error(request, error, extra_tags=tag)

        goto = '/'

    return redirect(goto)

def create(request): 
    response = User.objects.registration_validator(request.POST)
    goto = Route.REDIRECT_ROUTE

    if response['status']:
        request.session['user_session']=response['user'].id

        clearSessions(request.session)
    else:
        request.session['name'] = request.POST['name']
        request.session['username'] = request.POST['username']
        
        for tag, error in response['errors'].iteritems():
            messages.error(request, error, extra_tags=tag)

        goto = '/register/'

    return redirect(goto)

def logout(request):
    del request.session['user_session']

    return redirect('/')

def clearSessions(session):
    if 'name' in session:
        del session['name']
    if 'username' in session:
        del session['username']