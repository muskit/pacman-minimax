from enum import Enum
import random
import pygame as pg
from pygame.sprite import Sprite

from vector import Vector

from ghost_ai import \
    GhostMode, get_next_move_tile, get_target_tile_inky, get_target_tile_blinky,\
    get_target_tile_clyde, get_target_tile_pinky, OPPOSITE_DIR
from util import *
from timer import Timer, TimerDict, TimerDual
import maze as mz
import application as app
import play as pl


class Ghost(Sprite):
    """Base class for the ghosts. Should not be instantiated!"""
    FRIGHTENED_SPEED = 3
    EATEN_SPEED = 20

    def __init__(
        self,
        name: str,
        color: tuple[int, int, int],
        type: str,
        tile_start: tuple[int, int],
        tile_scatter: tuple[int, int],
        maze, pacman, play
    ):
        super().__init__()
        self.name = name
        self.pacman = pacman
        self.maze = maze
        self.play = play
        self.rect = pg.Rect((0, 0), (mz.Maze.TILE_SIZE/2, mz.Maze.TILE_SIZE/2))
        
        self.tile_start = tile_start
        """The tile to spawn on at the very beginning of a game."""

        self.tile = tile_start
        """The ghost's last \"steady\" tile."""

        self.tile_next = None
        """The immediate tile for the ghost to move towards. Should be adjacent to `self.tile`."""

        self.tile_scatter = tile_scatter
        """The tile that the ghost will target during scatter mode."""

        self.target = tile_scatter
        """The tile that the ghost will ultimately be working towards."""

        self.tile_progress = 1
        """Ghost's progress of movement between `self.tile`` and `self.next_tile`.
        Should range 0 to 1 inclusive."""

        self.facing = 'right'
        """Which way the ghost is currently facing."""

        self.mode: GhostMode = GhostMode.SCATTER
        """The ghost's current behavior mode. Refer to the `GhostMode` enum."""

        self.debug_draw_rect = pg.surface.Surface(size=(24, 24))
        self.debug_draw_rect.fill(color)

        ## SPRITES ##
        normal_sprites = {
            'up': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/{type}_up_{x}.png") for x in range(3, 5)],
            'down': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/{type}_down_{x}.png") for x in range(3, 5)],
            'left': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/{type}_left_{x}.png") for x in range(3, 5)],
            'right': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/{type}_right_{x}.png") for x in range(3, 5)]
        }
        eaten_sprites = {
            'up': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/dead_ghosts_eyes_up.png")],
            'down': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/dead_ghosts_eyes_down.png")],
            'left': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/dead_ghosts_eyes_left.png")],
            'right': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/dead_ghosts_eyes_right.png")]
        }
        frightened_sprites = {
            'blue': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/dead_ghosts_blue_{x}.png") for x in range(3, 5)],
            'white': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/dead_ghosts_white_{x}.png") for x in range(3, 5)]
        }
        
        self.normal_animator = TimerDict(dict_frames=normal_sprites, first_key='up')
        """The sprite animation handler for normal mode."""

        self.frightened_flickering_animator = TimerDual(frames1=frightened_sprites['blue'], frames2=frightened_sprites['white'], waitBetween=200)
        """The sprite animation handler for frightened mode (flickering)."""

        self.frightened_animator = Timer(frames=frightened_sprites['blue'])

        self.eaten_animator = TimerDict(dict_frames=eaten_sprites, first_key='up')
        """The sprite animation handler for eaten mode."""

        self.image = self.normal_animator.imagerect()
        self.update_next_tile()
        self.update_facing()

    def reset(self):
        self.mode = GhostMode.SCATTER
        self.tile = self.tile_start
        self.tile_next = None
        self.tile_progress = 1
        self.facing = 'right'
        self.target = self.tile_scatter
        self.update_next_tile()
        self.update_facing()
        self.update_rect()

    def set_mode(self, mode):
        if self.mode not in [GhostMode.EATEN, GhostMode.EATEN_INVISIBLE, GhostMode.GHOST_HOUSE_INSIDE, GhostMode.GHOST_HOUSE_JOINING, GhostMode.GHOST_HOUSE_LEAVING]:
            self.mode = mode
            self.flip()

    def update_chase_target(self) -> None:
        """OVERRIDE: Set the next target tile. Should only modify `self.target`!"""
        pass

    def update_next_tile(self):
        """Sets `self.next_tile` based on `self.target`."""
        self.tile_next = get_next_move_tile(
            from_tile=self.tile,
            target_tile=self.target,
            maze=self.maze,
            facing=self.facing,
            cur_mode=self.mode
        )
        # print(f'Tiles: {candidate_tiles}')
        # print(f'Dist: {dist}')
        # print(self.facing + '\n')
    
    def update_facing(self):
        """Update `self.facing` based on `self.tile` and `self.tile_next`."""
        self.facing = get_facing(self.tile, self.tile_next)

    def move(self):
        """Calculate target tile (if needed) and move towards it.
        Updates `self.facing` and `self.tile_next`."""

        # When next_tile is reached, update target and next_tile
        if self.tile_progress >= 1:
            self.tile_progress %= 1
            self.tile = (self.tile_next[0], self.tile_next[1])

            # determine target
            if self.mode == GhostMode.SCATTER:
                # scatter
                self.target = self.tile_scatter
            elif self.mode == GhostMode.CHASE:
                # chase
                self.update_chase_target()
            elif self.mode == GhostMode.EATEN:
                self.target = (13, 11)
                if self.tile == (13, 11):
                    self.mode = GhostMode.GHOST_HOUSE_JOINING
            # moving in/out the ghost house
            if self.mode == GhostMode.GHOST_HOUSE_JOINING:
                self.target = (13, 14)
                if self.tile == (13, 14):
                    self.mode = GhostMode.GHOST_HOUSE_LEAVING
            if self.mode == GhostMode.GHOST_HOUSE_LEAVING:
                self.target = (13, 11)
                if self.tile == (13, 11):
                    self.mode = self.play.play_state.mode_ghosts
                    self.flip()

            self.update_next_tile()
            self.update_facing()
        
        # Move towards next_tile
        if self.mode == GhostMode.FRIGHTENED:
            speed = Ghost.FRIGHTENED_SPEED
        elif self.mode == GhostMode.EATEN:
            speed = Ghost.EATEN_SPEED
        else:
            speed = self.play.ghosts_speed
        self.tile_progress += speed*app.Application.FRAME_TIME

        self.update_rect()
    
    def flip(self):
        """Flip our movement completely."""
        self.facing = OPPOSITE_DIR[self.facing]
        self.tile_temp = self.tile_next
        self.tile_next = self.tile
        self.tile = self.tile_temp
        self.tile_progress = 1 - self.tile_progress

    def update_rect(self):
        # print(self.tile_progress)
        current_tile = Vector(
            lerp(self.tile[0], self.tile_next[0], self.tile_progress),
            lerp(self.tile[1], self.tile_next[1], self.tile_progress)
        )
        px = mz.Maze.tile2pixelctr(current_tile)
        self.rect.center = (px.x, px.y)

    def draw(self):
        if self.play.play_state.hide_ghosts: return

        self.update_rect()

        # graphic retrieval
        if self.mode == GhostMode.FRIGHTENED: # frightened
            self.image = self.frightened_animator.imagerect()
            if self.play.play_state.frightened_timer <= 300:
                self.image = self.frightened_flickering_animator.imagerect()
        elif self.mode == GhostMode.EATEN_INVISIBLE: # just eaten (invisible)
            return
        elif self.mode in [GhostMode.EATEN, GhostMode.GHOST_HOUSE_JOINING]: # eaten (eyes)
            self.eaten_animator.key = self.facing
            self.image = self.eaten_animator.imagerect()
        else: # normal
            self.normal_animator.key = self.facing
            self.image = self.normal_animator.imagerect()

        # coordinates
        r = self.image.get_rect()
        r.center = self.rect.center
        self.maze.blit_relative(self.image, r)

        # DEBUG: draw current target
        target_vec = mz.Maze.tile2pixelctr(Vector(*self.target))
        target_pt = (target_vec.x, target_vec.y)
        target_rect = pg.Rect((0, 0), (24, 24))
        target_rect.center = target_pt
        self.maze.blit_relative(self.debug_draw_rect, target_rect)

    def update_mode(self):
        if self.mode == GhostMode.EATEN_INVISIBLE: self.mode = GhostMode.EATEN

    def update(self):
        self.update_mode()
        self.move()

class Blinky(Ghost):
    def __init__(self, maze, pacman, play):
        super().__init__(name='Blinky', color=(255, 0, 0), type='reds', tile_start=(18, 10), tile_scatter=(25, -4), maze=maze, pacman=pacman, play=play)
    
    def update_chase_target(self):
        self.target = get_target_tile_blinky(self.pacman.tile)

class Pinky(Ghost):
    def __init__(self, maze, pacman, play):
        super().__init__(name='Pinky', color=(255, 183, 255), type='pinks', tile_start=(8, 11), tile_scatter=(2, -4), maze=maze, pacman=pacman, play=play)
    
    def update_chase_target(self):
        self.target = get_target_tile_pinky(
            player_tile=self.pacman.tile,
            player_facing=self.pacman.facing
        )

class Inky(Ghost):
    def __init__(self, maze, pacman, play):
        super().__init__(name='Inky', color=(0, 255, 255), type='blues', tile_start=(18, 14), tile_scatter=(27, 31), maze=maze, pacman=pacman, play=play)
    
    def update_chase_target(self):
        self.target = get_target_tile_inky(
            player_tile=self.pacman.tile,
            blinky_tile=self.play.ghosts.sprites()[0].tile
        )

class Clyde(Ghost):
    def __init__(self, maze, pacman, play):
        super().__init__(name='Clyde', color=(255, 183, 81), type='oranges', tile_start=(9, 14), tile_scatter=(0, 31), maze=maze, pacman=pacman, play=play)
    
    def update_chase_target(self):
        self.target = get_target_tile_clyde(
            player_tile=self.pacman.tile,
            clyde_tile=self.tile,
            scatter_target_tile=self.tile_scatter
        )