from copy import deepcopy

from ghost_ai import *
import play as pl
from .model import *

def step(state: MState, direction: str) -> MState:
	"""
	Copies the state and simulates one step of the game, in which
	Pac Man moves to a tile.
	This assumes that Pac Man must ALWAYS move.

	If the tile Pac Man is moving to is not traversable or it's a
	terminal state, return None.
	"""
	if state.terminal: return None

	dest_tile =\
		(state.player.tile[0] + DIR_VECTOR[direction][0],
		state.player.tile[1] + DIR_VECTOR[direction][1])

	# traversable tile check
	tile_state = state.maze.get_tile_state(Vector(*dest_tile))
	if tile_state in [-1, 0, 4]: return None

	ret = deepcopy(state)

	# move pac man, consume tile
	ret.player.tile = dest_tile
	ret.consume_current_tile()

	# ghosts
	for g in ret.ghosts.values():
		g.step(
			ret.player,
			ret.ghosts,
			ret.maze
		)
	
	return ret


def explore_states(state: MState) -> list[MState]:
	"""
	Return dict[str, State] of next possible states (children tree nodes).
	Key is direction.
	Explores ONE layer/step in each valid direction.
	"""
	ret = {}
	for dir in ['up', 'down', 'left', 'right']:
		state = step(state, dir)
		if state != None:
			ret[dir] = state
	
	return ret


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

	# TESTING FUNCTIONS
	mplayer = MPlayer(play.player.tile, play.player.facing)
	st = MState(
		player=mplayer,
		maze=play.maze.maze,
		ghosts=play.ghosts,
		remaining_pellets=play.maze.remaining_pellets
	)
	print(f'{st}\n')
	explore_states(st)