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

	If the tile Pac Man is moving to is not traversable,
	return None.

	If the state is already terminal, return the same state, since
	nothing else can happen.
	"""
	if state.is_terminal(): return state

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


def evaluate(state: MState) -> int:
	"""
	Return utility score for state.
	
	Higher values are desirable.

	-∞ for death state,
	+∞ if state results in last pellet eaten (WIN!)
	"""
	player_state = state.player
	x1, y1 = player_state.tile
	state_value = 0

	# next_tile = tuple(map(sum, zip(player_state.tile, next_state_move[move])))
	next_tile_state = state.maze.consumed_tile
	# print(next_tile_state)
	# Checks what the following tile will be
	if next_tile_state == 1:
		state_value = state_value + 1
	elif next_tile_state == 2:
		state_value = state_value + 3
	elif next_tile_state == 3:
		state_value = state_value + 5
	elif next_tile_state == 5:
		state_value = state_value + 8

	# print(f'player tile: {player_state.tile}\n')
	# Check player position from the ghosts position
	nearest_ghost_position = 100
	for g in state.ghosts.values():
		x2, y2 = g.tile
		
		distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
		if distance < nearest_ghost_position:
			nearest_ghost_position = distance
			
	# 	print(f"{g.name} distance from pacman is {distance}")

	# print(f"nearestghost distance from pacman is {nearest_ghost_position}")
	if nearest_ghost_position >= 7:
		state_value = state_value + 0
	elif nearest_ghost_position >= 4:
		state_value = state_value - 10
	elif nearest_ghost_position >= 2:
		state_value = state_value - 15
	else:
		state_value = state_value - 20

	print(f"state {state_value}")

	return state_value



def minimax(state: MState, depth: int = 1) -> int:
	"""
	Recursive minimax function. Explores more states based on depth
	and returns an eval score.
	"""

	if depth <= 1 or state.is_terminal():
		return evaluate(state)
	
	value = -float('inf')
	for v in explore_states(state).values():
		value = max(minimax(v, depth-1), value)

	return value


def next_move(
	play,
	depth=1
) -> str:
	"""
	Use the minimax algorithm to determine best direction to travel in.
	Returns one of "up", "down", "left", or "right"
	"""

	st = MState(
		player=MPlayer(play.player.tile, play.player.facing),
		maze=play.maze.maze,
		ghosts=play.ghosts,
		remaining_pellets=play.maze.remaining_pellets
	)
	best = (-float('inf'), None) # (score: int, direction: str)
	for k, v in explore_states(st).items():
		scr = minimax(v, depth)
		if scr > best[0]:
			best = (scr, k)
	
	print(best[1])
	return best[1]
