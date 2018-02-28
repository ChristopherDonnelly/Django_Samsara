from __future__ import unicode_literals 
from django.shortcuts import render, HttpResponse, redirect 
from django.contrib import messages
from django.utils.html import escape
from .models import Game, Row, Square, Element, Entity, User
import json
from django.http import JsonResponse

def draw_board(request,game_id):
	context = {
		"game": Game.objects.get(id=game_id),
		"rows": Row.objects.filter(game_id=game_id),
		"user": User.objects.filter(id=request.session['user_session'])[0]
	}
	request.session['game_id'] = game_id
	return render(request, "game_board_app/board.html")
	
def index(request): 
	context = {
		"game": Game.objects.get(id=game_id),
		"user": User.objects.filter(id=request.session['user_session'])[0]
	}
	return render(request, "game_board_app/index.html", context)

# Create a new game
def populate_board(request):
	game = Game.objects.new_game(request.session['user_session'])['game']
	for row in game.rows.all():
		for square in row.squares.all():
			if square.entity:
				print (square.entity.kind, square.entity.element.name, square.entity.element.color)
	request.session['player_number'] = 1
	return redirect('draw_board/{}'.format(game.id))

def update_board(request):
	if request.method == 'POST':
		print (request.POST)
	return redirect('/game_board_app')

def place_building(request):
	game_id = request.session['game_id']
	body = json.loads(request.body.decode('utf-8'))
	if request.session['player_number'] == 1:
		row = 1
	else:
		row = 8
	building = Entity.objects.place_building(request.session['user_session'],game_id,row,body['column'],body['element'])

	if building['errors']:
		for tag, error in building['errors'].items():
			messages.error(request, error, extra_tags=tag)
	return JsonResponse({"success":True})

def attack(request,unit_id,target_id):
	Unit.attack(unit_id,target_id)

	return HttpResponse("Completed attack")

# When the player runs out of activity points
def complete_turn(request):
	# Units move one space each
	Game.objects.move_units(request.session['game_id'])

	# Every building with enough resources will produce a unit
	Game.objects.produce_units(request.session['game_id'])

	return HttpResponse("Completed turn")



