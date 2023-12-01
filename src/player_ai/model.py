from copy import deepcopy

from vector import Vector

from ghost import Ghost
from maze import Maze
import ghost_ai as g_ai

class MMaze:
	def __init__(self, cur_maze: list[str]):
		self.maze = deepcopy(cur_maze)

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
		state = self.get_tile_state(vec)
		strpos = Maze.tile2strpos(vec)

		if state == 2: # food pellet
			self.maze[strpos] = '1'
			# self.remaining_pellets -= 1
		elif state == 3: # power pellet
			self.maze[strpos] = '1'
			# self.remaining_pellets -= 1
		elif state == 5: # bonus fruit 
			self.maze[strpos] = '1'

class MGhost:
	def __init__(self, ghost: Ghost):
		self.name = ghost.name
		self.tile = ghost.tile
		self.facing = ghost.facing
	
	def step(self, player_tile: tuple[int, int], maze: MMaze):
		"""Simulate the ghost taking its next step"""
		match self.name:
			case "Blinky":
				pass
			case "Pinky":
				pass
			case "Inky":
				pass
			case "Clyde":
				pass

class MState:
	def __init__(self,
		player_tile: tuple[int, int],
		maze: list[str],
		ghosts: list[Ghost],
		remaining_pellets: int
	):
		"""Construct an AI-model state from existing game state."""
		self.tile = player_tile
		self.maze = MMaze(maze)
		self.ghosts: dict[MGhost] = {}
		for g in ghosts:
			self.ghosts[g.name] = MGhost(g)
		# Note: lower remaining_pellets is better for player!
		self.remaining_pellets = remaining_pellets
		self.terminal = False # TODO: determine if state is terminal