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
			player = Player.objects.create(game=game,user=User.objects.get(id=user_id),player_number=1)
			# Player1 is host of new game
			game.host.add(player)
			game.save()
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
			player = Player.objects.create(game=game,user=User.objects.get(id=user_id),player_number=2)

	def complete_turn(self,game_id):
		games = Game.objects.filter(id=game_id)
		if games.count() == 1:
			game = games[0]
			print("Turn: ",game.turn)
		else:
			errors['game'] = "No game or too many games found"

		game.move_units()
		game.produce_units()

		if game.turn == 1:
			game.turn = 2
		else:
			game.turn = 1
		game.save()

class Game(models.Model):
	level = models.PositiveSmallIntegerField()
	turn = models.PositiveSmallIntegerField(default=1) # Keeps track of whose turn it is
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

	objects = GameManager()

	def produce_units(self):
		buildings = self.player_units('Building').order_by('square__row__position')

		for building in buildings:
			building.produce_unit()

	def move_units(self):
		if self.turn == 1:
			units = self.player_units('Unit').order_by('-square__row__position')
		else:
			units = self.player_units('Unit').order_by('square__row__position')

		for unit in units:
			print("Unit {} {}".format(unit,unit.element.name))
			unit.move_unit()


	def player_units(self,kind):
		player = Player.objects.raw("SELECT p.* FROM game_board_app_player p, game_board_app_game g "\
			"WHERE p.player_number=g.turn AND p.game_id=g.id AND g.id="+str(self.id))
		if len(list(player)):
			return Entity.objects.filter(owner_id=player[0].user_id,square__in=Square.objects.filter(row__game_id=self.id),kind=kind)
		else:
			return Entity.objects.filter(owner_id=None)

	def attackEnemy(self):
		# Get the other player's object (the player whose turn it isn't)
		print("Attacking enemy!")
		enemies = Player.objects.filter(game_id=self.id).exclude(player_number=self.turn)
		if enemies.count() == 1:
			enemies[0].attack()
		else:
			print("No enemy player found")

class Player(models.Model):
	game = models.ForeignKey(Game, related_name="players",on_delete=models.PROTECT)
	hosted_games = models.ForeignKey(Game, related_name="host", null=True, on_delete=models.SET_NULL)
	user = models.ForeignKey(User,on_delete=models.PROTECT)
	player_number = models.PositiveSmallIntegerField()
	health = models.IntegerField(default=10)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

	def attack(self):
		self.health -= 1
		self.save()

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
		print ("Row {}, game {}, column {}, squares {}".format(row,game_id,column,squares.count()))
		if squares.count() == 1:
			square = squares[0]
		else:
			errors['square'] = "No square or too many squares found"

		if not errors:
			entity = Entity.objects.create(element=Element.objects.get(name=element),level=5,health=5,kind='Building',owner=User.objects.get(id=user_id))
			print(entity)
			square.entity = entity
			print (square)
			square.save()

		return {"errors":errors, "entity": entity}

# insert into game_board_app_entity (element_id,level,owner_id,created_at,updated_at,kind) values (1,1,1,'2/24/2018','2/24/2018','Building')
class Entity(models.Model):
	kind = models.CharField(max_length=50,default="Building")
	element = models.ForeignKey(Element, related_name="entity",on_delete=models.PROTECT)
	level = models.PositiveSmallIntegerField(default=1)
	health = models.PositiveSmallIntegerField(default=1)
	owner = models.ForeignKey(User, related_name="entity",on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

	def attack(self,target_entity):
		entity_relationship = { "fire": ["wood","metal"],
								"wood": ["earth","water"],
								"earth": ["water","fire"],
								"water": ["metal","fire"],
								"metal": ["wood","earth"]
								}

		if self.element == target_entity.element:
			self.health -= 1
			target_entity.health -= 1
		elif target_entity.element.name in entity_relationship[self.element.name]:
			target_entity.health -= 1
			print("Player ({}) beats target ({})".format(self.element.name,target_entity.element.name))
		else:
			self.health -= 1
			print("Player ({}) loses to target ({})".format(self.element.name,target_entity.element.name))

		self.save()
		target_entity.save()
		target_entity.check_unit()

	objects = EntityManager()

	def check_unit(self):
		if self.health == 0:
			# Unit has died; remove it from the board
			print("Removing unit {}, element:{}, owner:{}".format(self, self.element.name, self.owner.name))
			square = self.square
			square.entity = None
			square.save()
			self.delete()
			return False
		else:
			return True

	def move_unit(self):
		player_number = Player.objects.filter(user_id=self.owner_id).values('player_number')[0]['player_number']
		position = self.square.row.position
		
		if player_number == 1:
			new_position = position+1
		else:
			new_position = position-1

		# Check to make sure the destination square is empty
		new_squares = Square.objects.filter(row__game_id=self.square.row.game_id,row__position=new_position,position=self.square.position)		

		# If we're about to go off the game board
		if not new_squares:
			# If we're in the enemy's base row, we can do damage (though this unit will die)
			if self.square.inEnemyBaseRow(player_number):
				self.health = 0
				self.save()
				self.square.row.game.attackEnemy()
		# If the square we're trying to move into isn't empty
		elif new_squares[0].entity:
			# If this player doesn't own the unit, attack it
			if self.owner != new_squares[0].entity.owner:
				self.attack(new_squares[0].entity)

		# If we survived any attacks, move the unit forward
		if self.check_unit() and new_squares.count() == 1 and not new_squares[0].entity:
			new_square = new_squares[0]

			# Clear out the unit's current square
			prev_square = self.square
			prev_square.entity = None
			prev_square.save()

			# Set the contents of the new square
			new_square.entity = self
			new_square.save()

	def produce_unit(self):
		position = self.square.row.position
		game_id = self.square.row.game_id

		if position == 1:
			new_position = 2
		else:
			new_position = 7

		print("Producing for building {}".format(self.element.name))
		new_square = Square.objects.get(row__game_id=game_id,row__position=new_position,position=self.square.position)		
		if not new_square.entity:
			print("Producing for building {}, element:{}, owner:{}".format(self,self.element.name,self.owner.name))
			unit = Entity.objects.create(kind='Unit',element=self.element,owner=self.owner)
			# Set the contents of the new square
			new_square.entity = unit
			new_square.save()
		else:
			print("Found entity: {} {}".format(new_square.entity,new_square.entity.element.name))

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

	def inEnemyBaseRow(self,player_number):
		if player_number == 1:
			return self.row.position == 8
		else:
			return self.row.position == 1
