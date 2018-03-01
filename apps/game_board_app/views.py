from __future__ import unicode_literals 
from django.shortcuts import render, HttpResponse, redirect 
from django.contrib import messages
from django.utils.html import escape
from .models import Game, Row, Square, Element, Entity, User, Player
import json
from django.http import JsonResponse

def get_players_info(request):

	response = { }

	players = Player.objects.filter(game_id=request.session['game_id'])

	for player in players:
		user = User.objects.get(id=player.user_id)
		if user.id == request.session['user_session']:
			response['current_player'] = user.username
			response['current_player_health'] = player.health
			if player.game.turn == player.player_number:
				response['current_player_turn'] = True
			else:
				response['current_player_turn'] = False
		else:
			response['opponent'] = user.username
			response['opponent_health'] = player.health
			if player.game.turn == player.player_number:
				response['opponent_turn'] = True
			else:
				response['opponent_turn'] = False
		
		if player.game.turn == player.player_number:
			response['turn'] = user.username

	return JsonResponse(response)

def get_squares(request):
	game_id = request.session['game_id']
	reverse_order = False

	players = Player.objects.filter(game_id=game_id)

	for player in players:
		if player.user_id == request.session['user_session'] and player.player_number == 2:
			reverse_order=True

	all_rows = [[]] * 8
	
	row_count = -1
	square_count = -1

	rows=Row.objects.filter(game_id=game_id).order_by('-position')

	if reverse_order:
		rows.reverse()

	for row in rows:
		row_count += 1
		all_rows[row_count] = []
		
		for square in Square.objects.filter(row_id=row.id).order_by('position'):
			entity = Entity.objects.filter(id=square.entity_id)
			
			if len(entity):
				entity={
					'name': entity[0].element.name,
					'type': entity[0].kind.lower(),
					'image': entity[0].element.name.lower()+'_'+entity[0].kind.lower()
				}
			else:
				entity={
					'name': '',
					'type': '',
					'image': ''
				}

			space = {
				'square': square,
				'entity': entity
			}

			square_count += 1
			
			all_rows[row_count].append(space)

		if reverse_order:
			all_rows[row_count].reverse()

	if reverse_order:
		all_rows.reverse()

	context = {
		"game": Game.objects.get(id=game_id),
		"rows": all_rows,
		"user": User.objects.filter(id=request.session['user_session'])[0],
		'reverse_order': reverse_order
	}

	return render(request, "game_board_app/partials/game_squares.html", context)

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

	# --- Remove as this is controlled by the the button in HTML
	# if request.session['player_number'] == 1:
	# 	row = 1
	# else:
	# 	row = 8

	building = Entity.objects.place_building(request.session['user_session'],game_id,body['row'],body['column'],body['element'])

	if building['errors']:
		for tag, error in building['errors'].items():
			messages.error(request, error, extra_tags=tag)
	
	print(building['errors'])

	return JsonResponse({"success":True})

def attack(request,unit_id,target_id):
	Unit.attack(unit_id,target_id)

	return HttpResponse("Completed attack")

# When the player runs out of activity points
def complete_turn(request):
	# Units move one space each
	Game.objects.complete_turn(request.session['game_id'])

	return HttpResponse("Completed turn")



