from __future__ import unicode_literals 
 
from django.shortcuts import render, HttpResponse, redirect 
from django.utils.html import escape 
 
def index(request): 
    return render(request, "lobby_app/index.html") 
