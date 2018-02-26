from __future__ import unicode_literals 
 
from django.shortcuts import render, HttpResponse, redirect 
from django.utils.html import escape
from models import *
 
def index(request): 
	context = {
		"game": Game.objects.get(id=game_id),
		"user": User.objects.filter(id=request.session['user_session'])[0]
	}
	return render(request, "game_board_app/index.html", context)

def play(request,game_id):
	context = {
		"game": Game.objects.get(id=game_id),
		"rows": Row.objects.filter(game_id=game_id),
		"user": User.objects.filter(id=request.session['user_session'])[0]

	}
	return render(request, "game_board_app/game.html", context)

# Create a new game
def populate_board(request):
	game = Game.objects.new_game(request.session['user_session'])['game']
	for row in game.rows.all():
		for square in row.squares.all():
			if square.entity:
				print square.entity.kind, square.entity.element.name, square.entity.element.color
	return redirect('play/{}'.format(game.id))


def update_board(request):
	if request.method == 'POST':
		print request.POST
	return redirect('/game_board_app')
