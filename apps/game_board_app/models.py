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
<<<<<<< HEAD
			player = Player.objects.create(game=game,user=User.objects.get(id=user_id),player_number=2)

	def produce_units(self,game_id):
		buildings = Entity.objects.filter(square__in=Square.objects.filter(row__game_id=game_id),kind='Building')

		for building in buildings:
			print("Produce unit for ",building.id)
			building.produce_unit(game_id, building.id)

	def move_units(self,game_id):
		players = Player.objects.filter(game_id=game_id)

		for player in players:
			if player.player_number == 1:
				units = Entity.objects.player_units(player.id,game_id).order_by('-square__row__position')
			else:
				units = Entity.objects.player_units(player.id,game_id).order_by('-square__row__position')

			for unit in units:
				print("Move unit ",unit.id)
				unit.move_unit(game_id, unit.id)
=======
			player = Player.objects.create(game=game,user=User.objects.get(id=user_id),player_number=2,health=10)
>>>>>>> refs/remotes/origin/master

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
	health = models.IntegerField(default=10)
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

	def player_units(self,player_id,game_id):
		player = Player.objects.get(id=player_id)
		user = User.objects.get(id=player.user_id)
		return Entity.objects.filter(owner_id=user.id,square__in=Square.objects.filter(row__game_id=game_id),kind='Unit')

# insert into game_board_app_entity (element_id,level,owner_id,created_at,updated_at,kind) values (1,1,1,'2/24/2018','2/24/2018','Building')
class Entity(models.Model):
	kind = models.CharField(max_length=50,default="Building")
	element = models.ForeignKey(Element, related_name="entity",on_delete=models.PROTECT)
	level = models.PositiveSmallIntegerField(default=1)
	owner = models.ForeignKey(User, related_name="entity",on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

	def attack(self,unit_id,target_id):
		entity_relationship = { "fire": ["wood","metal"],
								"wood": ["earth","water"],
								"earth": ["water","fire"],
								"water": ["metal","fire"],
								"metal": ["wood","earth"]
								}
		errors = {}
		player_unit = None
		target_entity = None

		player_units = Entity.objects.filter(id=unit_id)
		if player_units.count() == 1:
			player_unit = player_units[0]
		else:
			errors['player_unit'] = "No unit or too many units found"

		target_entities = Entity.objects.filter(id=target_id)
		if target_entities.count() == 1:
			target_entity = target_entities[0]
		else:
			errors['target_entity'] = "No target or too many targets found"

		if not errors:
			result = None

			if player_unit.element == target_entity.element:
				print("Same element")
			elif target_entity.element.name in entity_relationship[player_unit.element.name]:
				print("Player ({}) beats target ({})").format(player_unit.element.name,target_entity.element.name)
			else:
				print("Player ({}) loses to target ({})").format(player_unit.element.name,target_entity.element.name)

		return errors

	objects = EntityManager()

	def move_unit(self,game_id,unit_id):
		player_number = Player.objects.filter(user_id=self.owner_id).values('player_number')[0]['player_number']
		unit = Entity.objects.get(id=unit_id)

		position = unit.square.row.position
		if player_number == 1:
			new_position = position+1
		else:
			new_position = position-1

		# Check to make sure the destination square is empty
		print("Move positions", game_id,new_position,unit.square.position,unit.id)
		new_squares = Square.objects.filter(row__game_id=game_id,row__position=new_position,position=unit.square.position)		
		if new_squares.count() == 1 and not new_squares[0].entity:
			new_square = new_squares[0]
			# Clear out the unit's current square
			prev_square = unit.square
			prev_square.entity = None
			prev_square.save()

			# Set the contents of the new square
			new_square.entity = unit
			new_square.save()

			print(new_square.entity)

			print("Moved unit ",unit.id)
		else:
			print(new_squares[0].entity)

	def produce_unit(self,game_id,building_id):
		player_number = Player.objects.filter(user_id=self.owner_id).values('player_number')[0]['player_number']
		building = Entity.objects.get(id=building_id)

		position = building.square.row.position
		if player_number == 1:
			new_position = 2
		else:
			new_position = 7

		print("Produce positions", game_id,new_position,building.square.position,building.id)
		new_square = Square.objects.get(row__game_id=game_id,row__position=new_position,position=building.square.position)		
		if not new_square.entity:
			unit = Entity.objects.create(kind='Unit',element=building.element,owner=building.owner)
			# Set the contents of the new square
			new_square.entity = unit
			new_square.save()

class Row(models.Model):
	position = models.PositiveSmallIntegerField() # Positions 1-5
	game = models.ForeignKey(Game, related_name="rows",on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

# insert into game_board_app_square (status,building_id,unit_id,position,row_id,created_at,updated_at) values ('Building',1,NULL,2,1,'2/24/2018','2/24/2018')
# update game_board_app_square set entity_id=NULL where id >= 1757 and id <= 1762
class Square(models.Model):
	entity = models.OneToOneField(Entity, related_name="square",null=True,on_delete=models.SET_NULL)
	position = models.PositiveSmallIntegerField() # Positions 1-10
	row = models.ForeignKey(Row, related_name="squares",on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)
