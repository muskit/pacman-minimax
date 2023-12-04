from copy import deepcopy
import math
import numpy as np

from ghost_ai import *
import play as pl
from .model import *

def manhattan_dist(a: tuple[int, int], b: tuple[int, int]):
	ret = np.sum(np.abs(np.array(a), np.array(b)))
	return ret

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
	if state.terminal() != TerminalState.ALIVE: return state

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

	if ret.terminal(): return ret

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
	# terminal state check
	match state.terminal():
		case TerminalState.DEAD:
			return -float('inf')
		case TerminalState.WIN:
			return float('inf')

	player = state.player
	x1, y1 = player.tile
	state_value = 0

	next_tile_state = state.maze.consumed_tile
	if next_tile_state == 1:
		state_value = state_value + 1
	elif next_tile_state == 2:
		state_value = state_value + 3
	elif next_tile_state == 3:
		state_value = state_value + 5
	elif next_tile_state == 5:
		state_value = state_value + 8

	# Check player position from the ghosts position
	nearest_ghost_dist = float('inf')
	for g in state.ghosts.values():
		if g.state == GhostMode.FRIGHTENED: continue

		x2, y2 = g.tile
		
		distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
		if distance < nearest_ghost_dist:
			nearest_ghost_dist = distance
	
	if nearest_ghost_dist == float('inf'):
		nearest_ghost_dist = 0

	ghost_scr = 0
	if nearest_ghost_dist <= 2:
		ghost_scr -=  200 * (2 - nearest_ghost_dist)
	elif nearest_ghost_dist <= 7:
		ghost_scr -= 2 * (12 - nearest_ghost_dist)
	# print(f'ghost_scr: {ghost_scr}')
	state_value += ghost_scr

	# nearest pellet
	break_flag = False
	nearest_pellet_dist = float('inf')
	for i in range(1, 100):
		for y in range(-i, i):
			for x in range(-i, i):
				if state.maze.get_tile_state(Vector(x1+x, y1+y)) in [2,3]:
					nearest_pellet_dist =\
						min(manhattan_dist((x, y), player.tile), nearest_pellet_dist)
					break_flag = True
					break
		if break_flag: break

	pellet_scr = -nearest_pellet_dist
	# print(f'pellet_scr: {pellet_scr}')
	state_value += pellet_scr
				
	# nearest power pellet
	# break_flag = False
	# for i in range(1, 100):
	# 	for y in range(-i, i):
	# 		for x in range(-i, i):
	# 			if state.maze.get_tile_state(Vector(x1+x, y1+y)) == 3:
	# 				power_scr = 0.25*(100-i)
	# 				print(f'power_scr: {power_scr}')
	# 				state_value += power_scr
	# 				break_flag = True
	# 				break
	# 		if break_flag: break
	# 	if break_flag: break

	return state_value

def minimax(state: MState, depth: int = 1) -> int:
	"""
	Recursive minimax function. Explores more states based on depth
	and returns an eval score.
	"""
	if depth <= 1 or state.terminal() != TerminalState.ALIVE:
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

	print('---------------')
	st = MState(
		player=MPlayer(play.player.tile, play.player.facing),
		maze=play.maze.maze,
		ghosts=play.ghosts,
		remaining_pellets=play.maze.remaining_pellets
	)
	opposite_dir = OPPOSITE_DIR[play.player.facing]

	best = (-float('inf'), None) # (score: int, direction: str)
	for k, v in explore_states(st).items():
		scr = minimax(v, depth)
		if k == opposite_dir:
			scr -= abs(scr)/10
		print(f'{k}={scr}\n')
		if scr > best[0]:
			best = (scr, k)
	print()
	
	print(f'{best[1]}\n')
	return best[1]
