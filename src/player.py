import random
import pygame as pg
from pygame.sprite import Sprite

from vector import Vector

from util import *
from timer import Timer, TimerDict, TimerDual
import maze as mz
import application as app
import play as pl
import ghost as gh

 
class Player(Sprite):
    """Class for the Player, handling Pac Man's controls, movement, and other operations."""
    DIR_VECTOR = {
        'up': (0, -1),
        'left': (-1, 0),
        'down': (0, 1),
        'right': (1, 0)
    }

    SPAWN_TILE = (12, 17)

    def __init__(self, maze: mz.Maze, play):
        super().__init__()
        self.maze = maze
        self.play = play
        self.rect = pg.Rect((0, 0), (mz.Maze.TILE_SIZE/2, mz.Maze.TILE_SIZE/2))

        player_sprites = {
            'up': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/pacs_up_{x}.png") for x in [1, 2, 1]],
            'down': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/pacs_down_{x}.png") for x in [1, 2, 1]],
            'left': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/pacs_left_{x}.png") for x in [1, 2, 1]],
            'right': [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/pacs_right_{x}.png") for x in [1, 2, 1]]
        }

        self.font = pg.font.Font(f'{app.Application.PROJECT_DIR}/resources/fonts/Press Start 2P.ttf', 24)

        player_all_closed_sprite = pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/pacs_all_closed.png")

        for v in player_sprites.values():
            v.insert(0, player_all_closed_sprite)

        self.pacman_animator = TimerDict(dict_frames=player_sprites, first_key='up', wait=48)
        """The sprite animation handler."""

        death_sprites = [pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/dead_pacs_{x}.png") for x in range(1, 12)]
        self.death_animator = Timer(death_sprites, looponce=True)

        """Sprite animation handler for Pac Man's death animation."""

        self.lives = 3
        """The player's remaining lives."""

        self.tile = (12, 17)
        """The player's last \"steady\" tile."""

        self.tile_next = (13, 17)
        """The immediate tile for the player to move towards. Should be adjacent to `self.tile`."""

        self.tile_progress = 0
        """Player's progress of movement between `self.tile`` and `self.next_tile`.
        Should range 0 to 1 inclusive."""

        self.eaten_ghost = None
        """Ghost being eaten."""

        self.hit = False

        self.death_phase = -1
        """Phase of Pac Man's death.
        
        -1: alive
        0: just got hit; action pause w/ pac man and ghosts visible
        1: action pause w/ just pac man visible
        2: animation running
        3: finally dead"""

        self.facing = ''
        self.update_facing()
        self.maze.consume_tile(self.tile)

    def ghost_interact(self, ghost: gh.Ghost):
        # eaten; do nothing
        if ghost.mode in [gh.GhostMode.EATEN, gh.GhostMode.EATEN_INVISIBLE]: return

        if ghost.mode == gh.GhostMode.FRIGHTENED: # frightened
            ghost.mode = gh.GhostMode.EATEN_INVISIBLE
            self.play.play_state.action_pause(50)
            self.play.sound.eat_ghost()
            self.play.scoreboard.increment_points_ghost()
            # TODO: replace pacman's sprite with score text
        else: # hostile in all its forms
            self.got_hit()
        
        self.play.sound.stop_chomping()

    def got_hit(self):
        """When Pac Man is hit by a ghost."""
        self.hit = True

    def update_facing(self):
        """Update `self.facing` based on `self.tile` and `self.tile_next`."""
        diff = (self.tile_next[0] - self.tile[0], self.tile_next[1] - self.tile[1])
        if diff == (0,0): return
        if diff[0] != 0: # horizontal movement
            self.facing = 'left' if diff[0] < 0 else 'right'
        else: # vertical movement
            self.facing = 'down' if diff[1] > 0 else 'up'
        
    def teleport(self, tile: tuple[int, int]):
        """Teleport Pac Man to a particular tile."""
        self.tile = tile
        self.tile_next = tile
        self.tile_next = self.get_facing_tile()
        self.tile_progress = 0
    
    def reset(self):
        """Runs after death animation is finished."""
        self.tile = Player.SPAWN_TILE
        self.tile_next = Player.SPAWN_TILE
        self.tile_progress = 0
        self.facing = 'right'
        self.update_tile_next()
        self.hit = False
        self.death_phase = -1
        self.death_animator.reset()
        self.pacman_animator.reset()
        pass

    def get_facing_tile(self, direction:str=None):
        if direction == None:
            vec = Player.DIR_VECTOR[self.facing]
        else:
            vec = Player.DIR_VECTOR[direction]     
        return (self.tile_next[0] + vec[0], self.tile_next[1] + vec[1])

    def update_tile_next(self):
        """Determine the next intermediate tile to go to. Should only run when we've reached target tile (self.tile_progress >= 1)"""
        self.tile = self.tile_next
        tile_check = self.get_facing_tile()
        tile_state = self.maze.get_tile_state(Vector(*tile_check))
        if tile_state not in [-1, 0, 4]:
            self.tile_next = tile_check

    def try_set_direction(self, direction: str):
        if self.tile_progress >= 0.8:
            state = self.maze.get_tile_state(Vector(*self.get_facing_tile(direction)))
            if state not in [-1, 0, 4]:
                self.facing = direction

    def update_rect(self):
        current_tile = Vector(
            lerp(self.tile[0], self.tile_next[0], self.tile_progress),
            lerp(self.tile[1], self.tile_next[1], self.tile_progress)
        )
        px = mz.Maze.tile2pixelctr(current_tile)
        self.rect.center = (px.x, px.y)

    def move(self):
        self.tile_progress += self.play.player_speed*app.Application.FRAME_TIME
        if self.tile_progress >= 1:
            self.tile_progress %= 1
            self.tile = [self.tile_next[0], self.tile_next[1]]
            self.maze.consume_tile(self.tile)
            self.update_tile_next()
            self.update_facing()
        self.update_rect()

    def dying(self):
        if self.death_phase == -1: # just got hit
            self.play.sound.stop_all()
            self.play.play_state.action_pause(60)
            self.death_phase = 0
        if self.death_phase == 0:
            if not self.play.play_state.is_action_pausing:
                self.play.play_state.hide_ghosts = True
                self.play.play_state.action_pause(30)
                self.death_phase = 1
                self.image = self.death_animator.imagerect()
        if self.death_phase == 1: # action pause w/ ghosts hidden
            if not self.play.play_state.is_action_pausing:
                # PLAY DEATH SOUND
                self.play.sound.music_death()
                self.play.play_state.action_pause(60*2)
                self.death_phase = 2
        if self.death_phase == 2:
            if not self.play.play_state.is_action_pausing:
                self.lives -= 1
                self.play.reset()

    def draw(self):
        self.update_rect()
        self.pacman_animator.key = self.facing
        
        if self.death_phase == -1:
            self.image = self.pacman_animator.imagerect()
        elif self.death_phase == 2:
            self.image = self.death_animator.imagerect()

        r = self.image.get_rect()
        r.center = self.rect.center
        # draw pacman
        self.maze.blit_relative(self.image, r)

        # draw lives
        for i in range(self.lives):
            img = self.pacman_animator.dict_frames['right'][1]
            r = img.get_rect()
            r.center = (720 + i*50, 200)
            self.maze.blit_relative(self.pacman_animator.dict_frames['right'][1], r)

    def update(self):
        if self.hit:
            self.dying()
        self.move()


