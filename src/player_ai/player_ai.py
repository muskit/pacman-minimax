from copy import deepcopy
import math
import numpy as np

from ghost_ai import *
import play as pl
from .model import *

def manhattan_dist(point1, point2):
    distance = 0
    for x1, x2 in zip(point1, point2):
        difference = x2 - x1
        absolute_difference = abs(difference)
        distance += absolute_difference

    return distance

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

	if ret.terminal() == TerminalState.DEAD: return ret

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
	p_x, p_y = player.tile
	state_value = 0

	# Check player position from the ghosts position
	ghost_scr = 0
	for g in state.ghosts.values():
		if g.state not in [GhostMode.CHASE, GhostMode.SCATTER]: continue

		# x2, y2 = g.tile
		
		# dist_squared = (x2 - x1)**2 + (y2 - y1)**2
		dist = manhattan_dist(g.tile, player.tile)
		ghost_scr -= 120/dist

	print(f'ghost_scr: {ghost_scr}')
	state_value += ghost_scr

	# check consumed tile
	next_tile_state = state.maze.consumed_tile
	consume_scr = 0
	if next_tile_state == 2:
		consume_scr = 10
	elif next_tile_state == 3:
		consume_scr = 20
	elif next_tile_state == 5:
		consume_scr = 8
	
	print(f'consume_scr: {consume_scr}')
	state_value += consume_scr

	# nearest pellet
	pellet_layer_found = False
	nearest_pellet_dist = float('inf')
	for i in range(1, 100):
		for y in range(-i, i):
			for x in range(-i, i):
				tile = (p_x+x, p_y+y)
				if state.maze.get_tile_state(Vector(*tile)) in [2,3,5]:
					nearest_pellet_dist =\
						min(manhattan_dist(tile, player.tile), nearest_pellet_dist)
					pellet_layer_found = True
		if pellet_layer_found: break

	pellet_scr = -nearest_pellet_dist
	print(f'pellet_scr: {pellet_scr}')
	state_value += pellet_scr

	# number of pellets remaining in maze
	# remain_scr = 20 * (Maze.NUM_PELLETS - state.maze.remaining_pellets)
	# print(f'remain_scr: {remain_scr}')
	# state_value += remain_scr
				
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
	print(st)
	opposite_dir = OPPOSITE_DIR[play.player.facing]

	best = (-float('inf'), None) # (score: int, direction: str)
	possible_states = explore_states(st)
	for k, v in possible_states.items():
		scr = minimax(v, depth)
		if k == opposite_dir:
			scr -= abs(scr)/2
		print(f'{k}={scr}\n')
		if scr > best[0]:
			best = (scr, k)
	print()
	
	if best[1] == None:
		best = (-float('inf'), random.choice(list(possible_states.keys())))

	print(f'{best[1]}\n')
	return best[1]
