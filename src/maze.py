
import math
import numpy
import pygame as pg
from pygame import Surface
from pygame.sprite import Sprite

from timer import Timer
from util import clip

import application as app
from vector import Vector
import ghost as gh

class Maze(Sprite):

    FRESH_MAZE = (
        '0000000000000000000000000000'
        '0222222222222002222222222220'
        '0200002000002002000002000020'
        '0300002000002002000002000030'
        '0200002000002002000002000020'
        '0222222222222222222222222220'
        '0200002002000000002002000020'
        '0200002002000000002002000020'
        '0222222002222002222002222220'
        '0000002000001001000002000000'
        '0000002000001001000002000000'
        '0000002001111111111002000000'
        '0000002001000440001002000000'
        '0000002001011111101002000000'
        '1611112111011111101112111171'
        '0000002001011111101002000000'
        '0000002001000000001002000000'
        '0000002001111151111002000000'
        '0000002001000000001002000000'
        '0000002001000000001002000000'
        '0222222222222002222222222220'
        '0200002000002002000002000020'
        '0200002000002002000002000020'
        '0322002222222112222222002230'
        '0002002002000000002002002000'
        '0002002002000000002002002000'
        '0222222002222002222002222220'
        '0200000000002002000000000020'
        '0200000000002002000000000020'
        '0222222222222222222222222220'
        '0000000000000000000000000000'
    )

    WIDTH, HEIGHT = 28, 31
    TILE_SIZE = 24 # 24x24px square
    PORTAL_A_TILE = (1, 14)
    PORTAL_B_TILE = (26, 14)

    @staticmethod
    def pixel2tile(px_vec: Vector):
        """Converts a pixel-scaled Vector into a tile-scaled Vector."""
        return px_vec/Maze.TILE_SIZE
    
    @staticmethod
    def tile2pixel(tile_vec: Vector):
        """Converts a tile-scaled Vector into a pixel-scaled Vector."""
        return tile_vec*Maze.TILE_SIZE
    
    @staticmethod
    def tile2pixelctr(tile_vec: Vector):
        """Returns the center pixel of a tile."""
        return tile_vec*Maze.TILE_SIZE + Vector(12, 12)

    @staticmethod
    def tile2strpos(tile_vec: Vector):
        """Converts a tile vector into its position in the maze string."""
        x, y = math.floor(tile_vec.x), math.floor(tile_vec.y)
        return x + Maze.WIDTH*y
        
    def __init__(self, play):
        self.play = play
        self.surface: Surface = play.screen
        self.maze = list(Maze.FRESH_MAZE)
        self.image = pg.image.load(app.Application.PROJECT_DIR + '/resources/sprites/maze.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = numpy.subtract(self.surface.get_rect().center, self.rect.center)

        self.remaining_pellets = 244
        """Pellets left to eat before moving to the next level."""

        # edible sprites
        self.debug_tile = pg.surface.Surface(size=(20, 20))
        self.debug_tile.fill((34, 34, 34))
        self.debug_tile.set_alpha(230)
        self.food_pellet = pg.surface.Surface(size=(6, 6))
        self.food_pellet.fill((255, 183, 174))
        power_sprites = [
            pg.image.load(app.Application.PROJECT_DIR + '/resources/sprites/power_food.png'),
            pg.surface.Surface(size=(48, 48))
        ]
        power_sprites[1].set_alpha(0)
        self.power_pellet = Timer(frames=power_sprites, wait=10*1000*app.Application.FRAME_TIME)

        self.bonus_fruit_sprite = {
            'bonus_fruit': pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/special_food.png"),
        }

        self.portal_sprites = {
            'portal_a': pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/in_blue_portal.png"),
            'portal_b': pg.image.load(f"{app.Application.PROJECT_DIR}/resources/sprites/out_orange_portal.png")
        }
    
    def get_tile_state(self, tile_vec: Vector):
        """Returns the state of a tile.

        Possible return values:
        -1: out of bounds
        0: wall (non-traversable)
        1: empty
        2: food pellet
        3: power pellet
        4: ghost house entrance
        5: bonus fruit
        6: portal a
        7: portal b
        8: dot_food_points = 10
        9: power_pellet_points = 50
        10: bonus_fruit = 100
        11: ghost_points = 200 """
        
        if not ((0 <= tile_vec.x and tile_vec.x < Maze.WIDTH) or\
            (0 <= tile_vec.y and tile_vec.y < Maze.HEIGHT)):
            return -1
        strpos = Maze.tile2strpos(tile_vec)
        return int(self.maze[strpos])
    
    def consume_tile(self, tile_vec: tuple[int, int]):
        """Change tile state at `tile_vec`, set other game states."""
        vec = Vector(*tile_vec)
        state = self.get_tile_state(vec)
        strpos = Maze.tile2strpos(vec)

        if state in [-1, 0]: # (eating inaccessible tile)
            pass
        elif state == 1: # blank tile
            self.play.sound.stop_chomping()
        elif state == 2: # food pellet
            self.maze[strpos] = '1'
            self.play.sound.start_chomping()
            self.remaining_pellets -= 1
            self.play.scoreboard.increment_points_dot()
            # TODO: change score, counters
        elif state == 3: # power pellet
            self.maze[strpos] = '1'
            self.play.set_ghosts_mode(gh.GhostMode.FRIGHTENED)
            self.play.play_state.power_pellet_eatened()
            self.play.sound.music_power_pellet()
            self.remaining_pellets -= 1
            self.play.scoreboard.increment_points_power_pellet()
            # TODO: change score, counters, flee state
        elif state == 5: # bonus fruit 
            self.maze[strpos] = '1'
            self.play.scoreboard.increment_points_fruit()
            self.play.sound.music_eat_fruit()
        elif state == 6: # portal a
            self.play.player.teleport(Maze.PORTAL_B_TILE)
        elif state == 7: # portal b
            self.play.player.teleport(Maze.PORTAL_A_TILE)

    def reset(self):
        self.maze = list(Maze.FRESH_MAZE)
        self.remaining_pellets = 244
    
    def blit_relative(self, surface: Surface, rect: pg.Rect):
        r = rect.copy()
        r.center = (rect.center[0] + self.rect.left, rect.center[1] + self.rect.top)
        self.surface.blit(surface, r)

    def draw(self, draw_tiles = True):
        """Draw maze walls, as well as remaining consumables in play."""
        self.surface.blit(self.image, self.rect)
        if not draw_tiles: return
        
        for y in range(Maze.HEIGHT):
            for x in range(Maze.WIDTH):
                state = self.get_tile_state(Vector(x, y))
                # if state in [0, 1, 4]: continue # skip non-consumables
                # if state in [1, 4]: continue # ---DEBUG---

                tile_ctr = Maze.tile2pixelctr(Vector(x, y))
                # if state == 0: # ---DEBUG---
                #     rect = self.debug_tile.get_rect()
                #     rect.center = (tile_ctr.x, tile_ctr.y)
                #     self.blit_relative(self.debug_tile, rect)
                if state == 2: # food pellet
                    rect = self.food_pellet.get_rect()
                    rect.center = (tile_ctr.x, tile_ctr.y)
                    self.blit_relative(self.food_pellet, rect)
                elif state == 3:
                    img:Surface = self.power_pellet.imagerect()
                    rect = img.get_rect()
                    rect.center = (tile_ctr.x, tile_ctr.y)
                    self.blit_relative(img, rect)
                elif state == 5:
                    img = self.bonus_fruit_sprite['bonus_fruit']
                    rect = img.get_rect()
                    rect.center = (tile_ctr.x, tile_ctr.y)
                    self.blit_relative(img, rect)
                elif state == 6:
                    img = self.portal_sprites['portal_a']
                    rect = img.get_rect()
                    rect.center = (tile_ctr.x, tile_ctr.y)
                    self.blit_relative(img, rect)
                elif state == 7:
                    img = self.portal_sprites['portal_b']
                    rect = img.get_rect()
                    rect.center = (tile_ctr.x, tile_ctr.y)
                    self.blit_relative(img, rect)
                
                    

    def update(self):
        self.draw()