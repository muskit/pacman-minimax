from __future__ import annotations
from copy import deepcopy
from util import get_facing

from vector import Vector

from ghost import Ghost
from maze import Maze
from ghost_ai import *

class MMaze:
	def __init__(self, cur_maze: list[str], remaining_pellets: int, consumed_tile: int = None):
		# how much left to eat -- lower is better
		self.remaining_pellets = remaining_pellets
		self.maze = deepcopy(cur_maze)
		
		# WARNING: only correct if consume_tile was called at active tile ONCE prior to read!
		self.consumed_tile = consumed_tile

	def get_tile_state(self, tile_vec: Vector):
		"""Refer to `Maze.get_tile_state`"""
		if not ((0 <= tile_vec.x and tile_vec.x < Maze.WIDTH) or\
			(0 <= tile_vec.y and tile_vec.y < Maze.HEIGHT)):
			return -1
		strpos = Maze.tile2strpos(tile_vec)
		return int(self.maze[strpos])

	def consume_tile(self, tile: tuple[int, int]):
		"""Change tile state at `tile_vec`."""
		vec = Vector(*tile)
		self.consumed_tile = self.get_tile_state(vec)
		strpos = Maze.tile2strpos(vec)

		if self.consumed_tile in [2, 3]: # food/power pellet
			self.remaining_pellets -= 1
			self.maze[strpos] = '1'
		elif self.consumed_tile == 5: # bonus fruit 
			self.maze[strpos] = '1'

class MPlayer:
	def __init__(self, tile: tuple[int, int], facing: str):
		self.tile = tile
		self.facing = facing
	
	def move_to(self, tile: tuple[int, int]):
		self.facing = get_facing(self.tile, tile)
		self.tile = tile

class MGhost:
	def __init__(self, ghost: Ghost):
		self.name = ghost.name
		self.tile = ghost.tile
		self.facing = ghost.facing
	
	def step(
		self,
		player:MPlayer,
		ghosts: dict[str, MGhost],
		maze: MMaze
	):
		"""Simulate the ghost taking its next step"""
		target_tile: tuple[int, int]
		match self.name:
			case "Blinky":
				target_tile = get_target_tile_blinky(player.tile)
			case "Pinky":
				target_tile = get_target_tile_pinky(
					player_tile=player.tile,
					player_facing=player.facing
				)
			case "Inky":
				target_tile = get_target_tile_inky(
					player_tile=player.tile,
					blinky_tile=ghosts["Blinky"].tile
				)
			case "Clyde":
				target_tile = get_target_tile_clyde(
					player_tile=player.tile,
					clyde_tile=self.tile,
					scatter_target_tile=(0, 31)
				)

		next_tile = get_next_move_tile(
			from_tile=self.tile,
			target_tile=target_tile,
			maze=maze,
			facing=self.facing
		)
		self.facing = get_facing(self.tile, next_tile)
		self.tile = next_tile

class MState:
	def __init__(self,
		player: MPlayer,
		maze: list[str],
		ghosts: list[Ghost],
		remaining_pellets: int
	):
		"""Construct an AI-model state from existing game state."""
		self.player = player
		self.maze = MMaze(maze, remaining_pellets)
		self.ghosts: dict[str, MGhost] = {}
		for g in ghosts:
			self.ghosts[g.name] = MGhost(g)

	def is_terminal(self):
		if self.maze.remaining_pellets == 0:
			return True

		for g in self.ghosts.values():
			if g.tile == self.player.tile:
				return True
			
		return False

	def consume_current_tile(self):
		self.maze.consume_tile(self.player.tile)
	
	def __repr__(self):
		maze = deepcopy(self.maze.maze)
		maze[Maze.tile2strpos(Vector(*self.player.tile))] = "P"
		for k, g in self.ghosts.items():
			maze[Maze.tile2strpos(Vector(*g.tile))] = k[0]
		
		ret = ""
		for y in range(0, Maze.HEIGHT):
			for x in range(0, Maze.WIDTH):
				char = maze[Maze.WIDTH*y + x]
				char = " " if char == "1" else char
				char = "." if char == "2" else char
				ret += f' {char} '
			ret += '\n'
		return ret