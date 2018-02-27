from __future__ import unicode_literals 
from django.shortcuts import render, HttpResponse, redirect 
from django.utils.html import escape 
from ..game_board_app.models import *

def index(request): 
	context = {
		"games": Game.objects.all(),
		"user": User.objects.filter(id=request.session['user_session'])[0]
	}
	return render(request, "lobby_app/index.html", context)

def delete_board(request,game_id):
	Game.objects.delete_game(game_id)
	return redirect('/lobby')

def join_game(request,game_id):
	Game.objects.join_game(game_id,request.session['user_session'])
	request.session['player_number'] = 2
	return redirect('/game_board/draw_board/'+game_id)