from enum import Enum
import random

from vector import Vector

class GhostMode(Enum):
    SCATTER = 1
    CHASE = 2
    FRIGHTENED = 3
    EATEN_INVISIBLE = 4
    EATEN = 5
    GHOST_HOUSE_JOINING = 6
    GHOST_HOUSE_INSIDE = 7
    GHOST_HOUSE_LEAVING = 8

OPPOSITE_DIR = {
    'up': 'down',
    'left': 'right',
    'down': 'up',
    'right': 'left'
}

DIR_VECTOR = {
    'up': (0, -1),
    'left': (-1, 0),
    'down': (0, 1),
    'right': (1, 0)
}

def get_target_tile_blinky(player_tile: tuple[int, int]):
	return player_tile

def get_target_tile_pinky(
	player_tile: tuple[int, int],
	player_facing: str
):
	vec_facing = DIR_VECTOR[player_facing]
	tile_pac = list(player_tile)
	for i in range(2):
		tile_pac[i] += 4*vec_facing[i]
	return tuple(tile_pac)

def get_target_tile_inky(
	player_tile: tuple[int, int],
	blinky_tile: tuple[int, int]
):
	pivot = player_tile
	vec_diff = Vector(*pivot) - Vector(*blinky_tile)
	vec_diff.setidx(1, vec_diff.y*-1)
	return (pivot[0] + vec_diff.x, pivot[1] + vec_diff.y)

def get_target_tile_clyde(
	player_tile: tuple[int, int],
	clyde_tile: tuple[int, int],
	scatter_target_tile: tuple[int, int]
):
	d = Vector.distance_squared(Vector(*clyde_tile), Vector(*player_tile))
	if d < 64:
		return scatter_target_tile
	else:
		return player_tile

def get_next_move_tile(
	from_tile: tuple[int, int],
	target_tile: tuple[int, int],
	maze,
	facing: str = None,
	cur_mode: GhostMode = GhostMode.CHASE
):
	candidate_dirs = ['up', 'left', 'down', 'right']
	if facing != None:
		opposite_dir = OPPOSITE_DIR[facing]
		opposite_tile =\
			(from_tile[0]+DIR_VECTOR[opposite_dir][0], from_tile[1]+DIR_VECTOR[opposite_dir][1])
		candidate_dirs.remove(opposite_dir)
	candidate_tiles = {}
	dist = {}

	# wall check
	for dir in candidate_dirs:
		vec = DIR_VECTOR[dir]
		check_tile = (from_tile[0]+vec[0], from_tile[1]+vec[1])
		state = maze.get_tile_state(Vector(check_tile[0], check_tile[1]))
		if state in [0, -1, 6, 7] or \
			(cur_mode not in [GhostMode.GHOST_HOUSE_JOINING, GhostMode.GHOST_HOUSE_LEAVING] and state == 4):
			# skip non-traversable, and if not in eaten
			# state, skip ghost house entrance.
			continue
		candidate_tiles[dir] = check_tile
		dist[dir] = Vector.distance_squared(Vector(*check_tile), Vector(*target_tile))
	
	if len(candidate_tiles) > 0:
		if cur_mode == GhostMode.FRIGHTENED:
			# frightened; pick random tile
			chosen_dir = random.choice(list(candidate_tiles.keys()))
		else:
			# go towards target
			chosen_dir = min(dist, key=dist.get)
	else:
		chosen_dir = opposite_dir

	return candidate_tiles[chosen_dir] if chosen_dir != opposite_dir else opposite_tile