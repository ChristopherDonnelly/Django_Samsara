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
			game = Game.objects.create(level=level,turn=1)
			player = Player.objects.create(game=game,user=User.objects.get(id=user_id),player_number=1,health=10,resources=50)
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
		errors = {}
		game = Game.objects.filter(id=game_id)
		if game.count() == 1:
			Entity.objects.filter(square__in=Square.objects.filter(row__in=Row.objects.filter(game_id=game_id))).delete()
			Square.objects.filter(row__in=Row.objects.filter(game=Game.objects.get(id=game_id))).delete()
			Row.objects.filter(game=Game.objects.get(id=game_id)).delete()
			Player.objects.filter(game_id=game_id).delete()
			Game.objects.get(id=game_id).delete()
		else:
			errors['game'] = "No game or too many games found."
		return {"errors": errors}

	def join_game(self,game_id,user_id):
		game_check = Game.objects.check_game_id(game_id)
		game = game_check['game']
		errors = game_check['errors']

		if not errors:
			users = User.objects.filter(id=user_id)
			if users.count() == 1:
				user = users[0]
			else:
				errors['user'] = "No user or too many users found"

			if not errors:
				player = Player.objects.create(game=game,user=User.objects.get(id=user_id),player_number=2,health=10,resources=50)

		return {"errors": errors}

	def complete_turn(self,game_id):
		game_check = Game.objects.check_game_id(game_id)
		game = game_check['game']

		if not game_check['errors']:
			game.move_units()
			#game.produce_units()

			if game.turn == 1:
				game.turn = 2
			else:
				game.turn = 1
			game.save()

		return {"errors": game_check['errors'], "winner":game_check['winner']}

	def check_game_id(self,game_id):
		errors = {}
		game = None
		winner = None

		games = Game.objects.filter(id=game_id)
		if games.count() == 1:
			game = games[0]
			print("Turn: ",game.turn)
		else:
			errors['game'] = "No game or too many games found"

		if game and game.isOver():
			errors['game_over'] = "This game is over."
			players = Player.objects.filter(game=game).order_by('-health')[:1]
			winner = players[0].user.username

		return {"errors":errors, "game":game, "winner":winner}

	def produce_unit(self,game_id,user_id,building_id):
		game_check = Game.objects.check_game_id(game_id)
		game = game_check['game']
		errors = game_check['errors']
		player = None

		players = Player.objects.filter(game_id=game_id,user_id=user_id)
		if players.count() == 1:
			player = players[0]
		else:
			errors['player'] = "No player or too many players found"

		entities = Entity.objects.filter(id=building_id,owner_id=user_id,square__row__game_id=game_id)
		print("Building {}, Owner {}, game id {}".format(building_id,user_id,game_id))
		if entities.count() == 1:
			building = entities[0]
		else:
			errors['entity'] = "No entity or too many entities found"

		if not errors:
			if player.resources >= building.level:
				produced = building.produce_unit(building.level)
				if produced:
					player.resources -= building.level
					player.save()
				else: 
					errors['board'] = "Could not add unit to the board"
			else:
				errors['resources'] = "Not enough resources to produce from this building"
		return {"errors":errors, "winner":game_check['winner']}

	def upgrade_unit(self,game_id,user_id,building_id):
		game_check = Game.objects.check_game_id(game_id)
		game = game_check['game']
		errors = game_check['errors']
		player = None

		players = Player.objects.filter(game_id=game_id,user_id=user_id)
		if players.count() == 1:
			player = players[0]
		else:
			errors['player'] = "No player or too many players found"

		entities = Entity.objects.filter(id=building_id,owner_id=user_id,square__row__game_id=game_id)
		print("Building {}, Owner {}, game id {}".format(building_id,user_id,game_id))
		if entities.count() == 1:
			building = entities[0]
		else:
			errors['entity'] = "No entity or too many entities found"

		if not errors:
			if player.resources >= 1:
				upgraded = building.upgrade_unit()
				if upgraded:
					player.resources -= 1
					player.save()
			else:
				errors['resources'] = "Not enough resources to upgrade this building"
		return {"errors":errors, "winner":game_check['winner']}

	def move_unit(self,game_id,unit_id):
		game_check = Game.objects.check_game_id(game_id)
		game = game_check['game']
		errors = game_check['errors']
		result = None

		entities = Entity.objects.filter(id=unit_id,square__row__game_id=game_id)
		if entities.count() == 1:
			unit = entities[0]
		else:
			errors['entity'] = "No entity or too many entities found"

		if not errors:
			result = unit.move_unit()

		return {"errors":errors, "result":result, "winner":game_check['winner']}

class Game(models.Model):
	level = models.PositiveSmallIntegerField()
	turn = models.PositiveSmallIntegerField() # Keeps track of whose turn it is
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

	objects = GameManager()

	def isOver(self):
		players = Player.objects.filter(game_id=self.id)
		for player in players:
			if player.health <= 0:
				return True
		return False

	# def produce_units(self):
	# 	buildings = self.player_units('Building').order_by('square__row__position')

	# 	for building in buildings:
	# 		building.produce_unit()

	def move_units(self):
		if self.turn == 1:
			units = self.player_units('Unit').order_by('-square__row__position')
		else:
			units = self.player_units('Unit').order_by('square__row__position')

		for unit in units:
			unit.move_unit()


	def player_units(self,kind):
		player = Player.objects.raw("SELECT p.* FROM game_board_app_player p, game_board_app_game g "\
			"WHERE p.player_number=g.turn AND p.game_id=g.id AND g.id="+str(self.id))
		if len(list(player)):
			return Entity.objects.filter(owner_id=player[0].user_id,square__in=Square.objects.filter(row__game_id=self.id),kind=kind)
		else:
			return Entity.objects.filter(owner_id=None)

	def attackEnemy(self,player_number,damage):
		# Get the other player's object (the player whose turn it isn't)
		enemies = Player.objects.filter(game_id=self.id).exclude(player_number=player_number)
		if enemies.count() == 1:
			print("damage",damage)
			enemies[0].attack(damage)
		else:
			print("No enemy player found")

class Player(models.Model):
	game = models.ForeignKey(Game, related_name="players",on_delete=models.PROTECT)
	hosted_games = models.ForeignKey(Game, related_name="host", null=True, on_delete=models.SET_NULL)
	user = models.ForeignKey(User,on_delete=models.PROTECT)
	player_number = models.PositiveSmallIntegerField()
	health = models.IntegerField()
	resources = models.IntegerField()
	created_at = models.DateTimeField(auto_now_add = True)
	updated_at = models.DateTimeField(auto_now = True)

	def attack(self,damage):
		print("damage",damage)
		self.health -= damage
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
		if squares.count() == 1:
			square = squares[0]
		else:
			errors['square'] = "No square or too many squares found"

		if not errors:
			if player.resources > 5:
				entity = Entity.objects.create(element=Element.objects.get(name=element),level=1,health=5,kind='Building',owner=User.objects.get(id=user_id))
				square.entity = entity
				square.save()
				player.resources -= 5
				player.save()
			else:
				errors['resources'] = "Not enough resources to build"

		return {"errors":errors, "entity": entity}

# insert into game_board_app_entity (element_id,level,owner_id,created_at,updated_at,kind) values (1,1,1,'2/24/2018','2/24/2018','Building')
class Entity(models.Model):
	kind = models.CharField(max_length=50)
	element = models.ForeignKey(Element, related_name="entity",on_delete=models.PROTECT)
	level = models.PositiveSmallIntegerField()
	health = models.PositiveSmallIntegerField()
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
		attack_result = None

		if self.element == target_entity.element:
			print("Player {} ties with target {}".format(self.element.name,target_entity.element.name))
			print("Health before: {}, damage {}, self-level:{}, target-health:{}".format(self.health,target_entity.level,self.level,target_entity.health))
			self.health -= target_entity.level
			target_entity.health -= self.level
			attack_result = "Tie"
			target_entity.save()
			self.save()
			target_entity.check_unit()
			self.check_unit()
		elif target_entity.element.name in entity_relationship[self.element.name]:
			print("Player ({}) beats target ({})".format(self.element.name,target_entity.element.name))
			print("Health before: {}, damage {}, self-level:{}, target-health:{}".format(self.health,1,self.level,target_entity.health))
			target_entity.health -= (self.level+1)
			self.health -= target_entity.level
			attack_result = "Win"
			target_entity.save()
			self.save()
			target_entity.check_unit()
			self.check_unit()
		else:
			print("Player ({}) loses to target ({})".format(self.element.name,target_entity.element.name))
			print("Health before: {}, damage {}, self-level:{}, target-health:{}".format(self.health,target_entity.level+1,self.level,target_entity.health))
			self.health -= (target_entity.level+1)
			target_entity.health -= self.level
			attack_result = "Lose"
			target_entity.save()
			self.save()
			target_entity.check_unit()
			self.check_unit()

		return attack_result

	objects = EntityManager()

	def check_unit(self):
		if self.health <= 0:
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
		position = self.square.row.position
		attack_result = None
		game_id = self.square.row.game_id
		player = Player.objects.get(user_id=self.owner_id,game_id=game_id)
		player_number = player.player_number

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
				self.square.row.game.attackEnemy(player_number,self.level)
		# If the square we're trying to move into isn't empty
		elif new_squares[0].entity:
			# If this player doesn't own the unit, attack it
			if self.owner != new_squares[0].entity.owner:
				print("{} attacking {} owned by {}".format(self, new_squares[0].entity, new_squares[0].entity.owner))
				attack_result = self.attack(new_squares[0].entity)

		# If we survived any attacks, move the unit forward
		if self and new_squares.count() == 1 and not new_squares[0].entity:
			new_square = new_squares[0]

			# Clear out the unit's current square
			prev_square = self.square
			prev_square.entity = None
			prev_square.save()

			# Set the contents of the new square
			new_square.entity = self
			new_square.save()

		return attack_result

	def produce_unit(self,building_level):
		unit = None
		position = self.square.row.position
		game_id = self.square.row.game_id

		if position == 1:
			new_position = 2
		else:
			new_position = 7

		new_square = Square.objects.get(row__game_id=game_id,row__position=new_position,position=self.square.position)		
		if not new_square.entity:
			unit = Entity.objects.create(kind='Unit',element=self.element,owner=self.owner,level=building_level,health=building_level+1)
			# Set the contents of the new square
			new_square.entity = unit
			new_square.save()

		return unit

	def upgrade_unit(self):
		self.level += 1
		self.health += 1
		self.save()
		return True

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
