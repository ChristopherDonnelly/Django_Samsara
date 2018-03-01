from __future__ import unicode_literals 
from django.shortcuts import render, HttpResponse, redirect 
from django.utils.html import escape 
from ..game_board_app.models import *

def index(request): 
	current_user = User.objects.filter(id=request.session['user_session'])[0]
	current_player = Player.objects.filter(user=current_user)
	curr_players_game = Game.objects.raw("SELECT * FROM game_board_app_game g JOIN game_board_app_player p ON g.id = p.game_id WHERE p.user_id={}".format(current_user.id))
	# hosted_games = Game.objects.filter(host__in=current_player)
	others_games = Game.objects.exclude(host__in=current_player) 
	# players_in_game = Players.objects.game
	all_games = Game.objects.all()
	
	print "*******"
	context = {
		"all_games": all_games,
		"user": User.objects.filter(id=request.session['user_session'])[0],
		"curr_players_game": curr_players_game,
		"others_games": others_games,
	}
	return render(request, "lobby_app/index.html", context)

def delete_board(request,game_id):
	# if logged-in player is same as player who created game => allow player to delete game
	Game.objects.delete_game(game_id)
	return redirect('/lobby')

def join_game(request,game_id):
	Game.objects.join_game(game_id,request.session['user_session'])
	request.session['player_number'] = 2
	return redirect('/game_board/draw_board/'+game_id)