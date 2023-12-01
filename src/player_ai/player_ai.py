from copy import deepcopy

import ghost_ai
import play as pl
from .model import *

def step(state: MState, direction: str) -> MState:
	"""
	Simulate one step of the game, where Pac Man moves to a tile.
	This assumes that Pac Man must ALWAYS move.

	If the tile Pac Man is moving to is not traversable, return None.
	"""


def state_explore(state: MState) -> list[MState]:
	"""
	Return dict[str, State] of next possible states (children tree nodes).
	Key is direction.
	Explores ONE layer/step in each valid direction.
	"""
	# Recommendation: use deepcopy() to make children states based on parent
	

def evaluate(state: MState) -> int:
	"""
	Return utility score for state.
	
	Higher values are desirable.

	-∞ for death state
	+∞ if state results in last pellet eaten (WIN!)
	"""

def minimax():
	"""Recursive minimax function."""

def next_move(
	play,
	depth=1
) -> str:
	"""
	Use the minimax algorithm to determine best direction to travel in.
	Returns one of "up", "down", "left", or "right"
	"""

	# test construction of State
	st = MState(
		player_tile=play.player.tile,
		maze=play.maze.maze,
		ghosts=play.ghosts,
		remaining_pellets=play.maze.remaining_pellets
	)