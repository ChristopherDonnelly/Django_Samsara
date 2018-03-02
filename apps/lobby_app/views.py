from __future__ import unicode_literals 
from django.shortcuts import render, HttpResponse, redirect 
from django.utils.html import escape 
from ..game_board_app.models import *
import copy

def index(request): 
	all_games = Game.objects.all()

	current_user = User.objects.filter(id=request.session['user_session'])[0]
	all_games = Game.objects.all()
	current_players = Player.objects.filter(user=current_user)
	# query filters out only current player's games
	curr_players_game = Game.objects.raw("SELECT * FROM game_board_app_game g JOIN game_board_app_player p ON g.id = p.game_id WHERE p.user_id={}".format(current_user.id))

	
	# deepcopy makes a copy of all games, so our edits will not affect all game objs
	others_games = copy.deepcopy(all_games)
	# iterate through all of the current_players games
	for player in current_players:
		others_games = others_games.exclude(id=player.game_id)
		
	# hosted_games = Game.objects.filter(host__in=current_players)
	# others_games = Game.objects.exclude(host__in=current_players) 
	'''
	^ alternatively, we can use .difference for others_games
	'''
	
	context = {
		"all_games": all_games,
		"user": User.objects.filter(id=request.session['user_session'])[0],
		"curr_players_game": curr_players_game,
		"others_games": others_games,
	}
	return render(request, "lobby_app/index.html", context)

def show_game_info(request, game_id):
	all_games = Game.objects.all()
	current_user = User.objects.filter(id=request.session['user_session'])[0]
	all_games = Game.objects.all()
	current_players = Player.objects.filter(user=current_user)
	curr_players_game = Game.objects.raw("SELECT * FROM game_board_app_game g JOIN game_board_app_player p ON g.id = p.game_id WHERE p.user_id={}".format(current_user.id))

	others_games = copy.deepcopy(all_games)
	for player in current_players:
		others_games = others_games.exclude(id=player.game_id)

	context = {
		"all_games": all_games,
		"user": User.objects.filter(id=request.session['user_session'])[0],
		"curr_players_game": curr_players_game,
		"others_games": others_games,
	}
	
	return render(request, "lobby_app/game_info.html", context)

def delete_board(request,game_id):
	# if logged-in player is same as player who created game => allow player to delete game
	Game.objects.delete_game(game_id)
	return redirect('/lobby')

def join_game(request,game_id):
	Game.objects.join_game(game_id,request.session['user_session'])
	request.session['player_number'] = 2
	return redirect('/game_board/draw_board/'+game_id)