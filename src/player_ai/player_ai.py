import ghost_ai
import play as pl

from .model import *

def next_move(
	play,
	depth=1
):
	"""Use the minimax algorithm to determine best tile to travel."""
	st = State(
		player_tile=play.player.tile,
		maze=play.maze.maze,
		ghosts=play.ghosts
	)
	print('constructed a model!')