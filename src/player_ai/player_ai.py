from copy import deepcopy

from ghost_ai import *
import play as pl
from .model import *
import math

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


def explore_states(state: MState) -> dict[str, MState]:
	"""
	Return dict[str, State] of next possible states (children tree nodes).
	Key is direction.
	Explores ONE layer/step in each valid direction.
	"""
	ret = {}
	for direction in ['up', 'down', 'left', 'right']:
		cur_state = step(state, direction)
		if cur_state != None:
			ret[direction] = cur_state
	
	return ret


def evaluate(move: str, state: MState) -> int:
	"""
	Return utility score for state.
	
	Higher values are desirable.

	-∞ for death state
	+∞ if state results in last pellet eaten (WIN!)
	"""
	player_state = state.player
	x1, y1 = player_state.tile
	state_value = 0
	next_state_move = {
		'left': (-1 , 0),
		'right': (1 , 0),
		'up': (0, -1),
		'down': (0, 1),
	}

	next_tile = tuple(map(sum, zip(player_state.tile, next_state_move[move])))
	next_tile_state = state.maze.get_tile_state(Vector(*next_tile))
	# Checks what the following tile will be
	if next_tile_state == 2:
		state_value = state_value + 1
	elif next_tile_state == 3:
		state_value = state_value + 2
	elif next_tile_state == 5:
		state_value = state_value + 3

	# print(f'player tile: {player_state.tile}\n')
	# Check player position from the ghosts position
	for g in state.ghosts.values():
		x2, y2 = g.tile
		# print(f'{g.name} tile: {g.tile} status\n')

		distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

		if distance == 1:
			state_value = state_value - 3
		elif distance == 2:
			state_value = state_value - 2
		elif distance > 4:
			state_value = state_value + 3	
		else:
			state_value = state_value + 1



	return state_value



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
	st = MState(
		player=MPlayer(play.player.tile, play.player.facing),
		maze=play.maze.maze,
		ghosts=play.ghosts,
		remaining_pellets=play.maze.remaining_pellets
	)
	# print(f'{st}\n')
	possible_states = explore_states(st)

	state_values = {
		'left': 0,
		'right': 0,
		'up': 0,
		'down': 0,
	}

	print("NEXT STATE")
	for move, state in possible_states.items():
		print(f"\nYIPPIE {move}")
		state_values[move] = evaluate(move, state)

	print("state vlues", state_values)
