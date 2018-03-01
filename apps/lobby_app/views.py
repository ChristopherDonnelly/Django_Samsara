from __future__ import unicode_literals 
from django.shortcuts import render, HttpResponse, redirect 
from django.utils.html import escape 
from ..game_board_app.models import *

def index(request): 
	# get all games
	# iterate through all games
	
	current_user = User.objects.filter(id=request.session['user_session'])[0]
	current_player = Player.objects.filter(user=current_user)
	hosted_games = Game.objects.filter(host__in=current_player)
	others_games = Game.objects.exclude(host__in=current_player)
	# players_in_game = Players.objects.game
	all_games = Game.objects.all()
	print all_games

	# gets all players in games currently
	for game in all_games:
		# print game.players.all()
		print game.players.first()
		print game.players.last()
		
	# print current_user
	# print player_hosting
	# for game in hosted_games:
	# 	print game.id
	# for game in others_games:
	# 	print game.id
	# # print other_games
	# print "********"
	context = {
		"all_games": all_games,
		"user": User.objects.filter(id=request.session['user_session'])[0],
		"hosted_games": hosted_games,
		"others_games": others_games
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