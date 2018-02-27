# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from ..users_app.models import User
import random

# Create your models here.
class GameManager(models.Manager):
	def new_game(self,user_id,level=0,rows=6,columns=8):
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
			player = Player.objects.create(game=game,user=User.objects.get(id=user_id),player_number=1,score=0)

			# Build the board
			for row_num in range(1,rows+1):
				row = Row.objects.create(position=row_num,game=game)
				for col_num in range(1,columns+1):
					square = Square.objects.create(position=col_num,row=row)

			# Choose buildings for player 1
			Game.objects.choose_buildings(game.id,user_id,1)

		return {"errors": errors, "game":game}

	def delete_game(self,game_id):
		Entity.objects.filter(square=Square.objects.filter(row=Row.objects.filter(game=Game.objects.get(id=game_id)))).delete()
		Square.objects.filter(row=Row.objects.filter(game=Game.objects.get(id=game_id))).delete()
		Row.objects.filter(game=Game.objects.get(id=game_id)).delete()
		Game.objects.get(id=game_id).delete()

	def choose_buildings(self,game_id,user_id,player_number):
		rows = Row.objects.filter(game_id=game_id)
		cols = rows[0].squares.count()
		if player_number == 1:
			row = 1
		else:
			row = rows.count()

		building_count = 2
		for col_num in range(1,cols+1):
			entity = None
			element = random.randint(0,5) # 0 will be no building
			if element != 0 and building_count > 0:
				building_count -= 1
				entity = Entity.objects.create(kind='Building',element=Element.objects.get(id=element),level=0,owner=User.objects.get(id=user_id))
				square = Square.objects.get(position=col_num,row=Row.objects.get(game=Game.objects.get(id=game_id),position=row))
				square.entity = entity
				square.save()

		return True

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
			player = Player.objects.create(game=game,user=User.objects.get(id=user_id),player_number=2,score=0)
			Game.objects.choose_buildings(game.id,user_id,2)


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
	score = models.IntegerField()
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

# insert into game_board_app_element (name,color,created_at,updated_at) values ('fire','red','2/24/2018','2/24/2018')
class Element(models.Model):
	name = models.CharField(max_length=50) # Fire, Earth, Water, Metal, Wood
	color = models.CharField(max_length=50)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

class EntityManager(models.Manager):
	def relative_square(player_number,row,column):
		row_conversion = [1,2,3,4,5,6,7,8]
		column_conversion = [1,2,3,4,5,6]
		if player_number == 1:
			return {"row": row, "column": column}
		else:
			return {"row":row_conversion[row*-1], "column": column_conversion[column*-1]}

	def place_building(self,user_id,game_id,row,square,element):
		errors = {}
		entity = None
		players = Player.objects.filter(user=User.objects.filter(id=user_id),game=Game.objects.filter(id=game_id))
		if players.count() == 1:
			player = players[0]
		else:
			errors['user'] = "No user or too many users found"

		squares = Square.objects.filter(row=Row.objects.filter(game_id=game_id,position=row),position=square)
		print ("Row {}, game {}, square {}".format(row,game_id,square))
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
	entity = models.ForeignKey(Entity, related_name="square",null=True,on_delete=models.PROTECT)
	position = models.PositiveSmallIntegerField() # Positions 1-10
	row = models.ForeignKey(Row, related_name="squares",on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
