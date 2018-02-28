# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from ..users_app.models import User
import random

# Create your models here.
class GameManager(models.Manager):
	def new_game(self,user_id,level=0,columns=6,rows=8):
		errors = {}
		user = None
		game = None

		users = User.objects.filter(id=user_id)
		if users.count() == 1:
			user = users[0]
		else:
			errors['user'] = "No user or too many users found"

		if not errors:
			game = Game.objects.create(level=level)
			player = Player.objects.create(game=game,user=User.objects.get(id=user_id),player_number=1,health=10)

			# Build the board
			for row_num in range(1,rows+1):
				row = Row.objects.create(position=row_num,game=game)
				for col_num in range(1,columns+1):
					square = Square.objects.create(position=col_num,row=row)

		return {"errors": errors, "game":game}

	def delete_game(self,game_id):
		Entity.objects.filter(square__in=Square.objects.filter(row__in=Row.objects.filter(game_id=game_id))).delete()
		Square.objects.filter(row__in=Row.objects.filter(game=Game.objects.get(id=game_id))).delete()
		Row.objects.filter(game=Game.objects.get(id=game_id)).delete()
		Player.objects.filter(game_id=game_id).delete()
		Game.objects.get(id=game_id).delete()

	def join_game(self,game_id,user_id):
		errors = {}
		games = Game.objects.filter(id=game_id)
		if games.count() == 1:
			game = games[0]
		else:
			errors['game'] = "No game or too many games found"

		users = User.objects.filter(id=user_id)
		if users.count() == 1:
			user = users[0]
		else:
			errors['user'] = "No user or too many users found"

		if not errors:
			player = Player.objects.create(game=game,user=User.objects.get(id=user_id),player_number=2,health=10)

class Game(models.Model):
	level = models.PositiveSmallIntegerField()
	turn = models.PositiveSmallIntegerField(default=1) # Keeps track of whose turn it is
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

	objects = GameManager()

class Player(models.Model):
	game = models.ForeignKey(Game, related_name="players",on_delete=models.PROTECT)
	user = models.ForeignKey(User,on_delete=models.PROTECT)
	player_number = models.PositiveSmallIntegerField()
	health = models.IntegerField()
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

# insert into game_board_app_element (name,color,created_at,updated_at) values ('fire','red','2/24/2018','2/24/2018')
class Element(models.Model):
	name = models.CharField(max_length=50) # Fire, Earth, Water, Metal, Wood
	color = models.CharField(max_length=50)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

class EntityManager(models.Manager):

	def place_building(self,user_id,game_id,row,column,element):
		errors = {}
		entity = None
		players = Player.objects.filter(user_id=user_id,game_id=game_id)
		if players.count() == 1:
			player = players[0]
		else:
			errors['user'] = "No user or too many users found"

		squares = Square.objects.filter(row__in=Row.objects.filter(game_id=game_id,position=row),position=column)
		print ("Row {}, game {}, square {}, squares {}".format(row,game_id,column,squares.count()))
		if squares.count() == 1:
			square = squares[0]
		else:
			errors['square'] = "No square or too many squares found"

		if not errors:
			entity = Entity.objects.create(element=Element.objects.get(name=element),level=0,kind='Building',owner=User.objects.get(id=user_id))
			square.entity = entity
			square.save()

		return {"errors":errors, "entity": entity}

# insert into game_board_app_entity (element_id,level,owner_id,created_at,updated_at,kind) values (1,1,1,'2/24/2018','2/24/2018','Building')
class Entity(models.Model):
	kind = models.CharField(max_length=50,default="Building")
	element = models.ForeignKey(Element, related_name="entity",on_delete=models.PROTECT)
	level = models.PositiveSmallIntegerField()	
	owner = models.ForeignKey(User, related_name="entity",on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

	objects = EntityManager()

class Row(models.Model):
	position = models.PositiveSmallIntegerField() # Positions 1-5
	game = models.ForeignKey(Game, related_name="rows",on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

# insert into game_board_app_square (status,building_id,unit_id,position,row_id,created_at,updated_at) values ('Building',1,NULL,2,1,'2/24/2018','2/24/2018')
class Square(models.Model):
	entity = models.ForeignKey(Entity, related_name="square",null=True,on_delete=models.SET_NULL)
	position = models.PositiveSmallIntegerField() # Positions 1-10
	row = models.ForeignKey(Row, related_name="squares",on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
