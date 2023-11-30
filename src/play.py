## This class will manage the main game play screen.
import pygame as pg
from pygame.surface import Surface

import game_events as ge
import maze as mz
import ghost as gh
from play_state import PlayState
import player
from sound import Sound
import scoreboard as sb

class Play:
    def __init__(self, app):
        self.app = app
        self.screen:Surface = app.screen
        self.scoreboard = sb.Scoreboard(play=self)
        self.maze = mz.Maze(play=self)
        self.play_state = PlayState(play=self)

        self.sound = Sound()

        self.font = pg.font.Font(f'{app.PROJECT_DIR}/resources/fonts/Press Start 2P.ttf', 24)
        
        self.ready_text = self.font.render("READY!", True, (255, 255, 0))
        self.ready_text_rect = self.ready_text.get_rect()
        self.ready_text_rect.center = (24*14, 24*14.5)

        self.clear_text = self.font.render("LEVEL CLEAR!", True, (255, 255, 0))
        self.clear_text_rect = self.ready_text.get_rect()
        self.clear_text_rect.center = (24*11, 24*6)

        self.game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        self.game_over_text_rect = self.ready_text.get_rect()
        self.game_over_text_rect.center = (24*12.5, 24*6)

        self.food_pellets = 170

        self.player_speed = 7
        """The player's movement speed, in tiles per second."""

        self.ghosts_speed = 7
        """The ghosts' movement speed, in tiles per second."""

        self.player = player.Player(maze=self.maze, play=self)

        self.ghosts = pg.sprite.Group(
            gh.Blinky(maze=self.maze, pacman=self.player, play=self),
            gh.Inky(maze=self.maze, pacman=self.player, play=self),
            gh.Pinky(maze=self.maze, pacman=self.player, play=self),
            gh.Clyde(maze=self.maze, pacman=self.player, play=self)
        )

        self.phase = 0
        """The phase of the game.
        
        0: New game
        1: Ready
        2: Player-controlled gameplay
        3: Finished game
        4: game over"""

    def set_ghosts_mode(self, mode):
        for g in self.ghosts:
            g.set_mode(mode)

    def collision_check(self):
        cols = pg.sprite.spritecollide(self.player, self.ghosts, False)
        if len(cols) > 0:
            g = cols[0]
            self.player.ghost_interact(g)
    
    def reset(self, new_round = False):
        if self.player.lives > 0:
            self.play_state.reset()
            self.player.reset()
            for g in self.ghosts:
                g.reset()

            if new_round: self.maze.reset()

            self.play_state.action_pause(120)
            self.phase = 1
        else:
            # GAME OVER
            self.scoreboard.save_high_score()
            self.play_state.action_pause(300)
            self.phase = 5
            pass

    def run(self):
        self.play_state.action_pause(150)
        self.sound.music_beginning()
        while True:
            self.screen.fill((0, 0, 0))
            ge.process_events(self)
            self.play_state.update()

            if self.phase == 0:
                self.scoreboard.update()
                self.maze.draw(draw_tiles=False)
                self.maze.blit_relative(self.ready_text, self.ready_text_rect)
                if not self.play_state.is_action_pausing:
                    self.phase = 1
                    self.play_state.action_pause(100)
            elif self.phase == 1:
                # waiting to move on from ready to gameplay
                self.scoreboard.draw()
                self.maze.draw()
                self.maze.blit_relative(self.ready_text, self.ready_text_rect)
                self.player.draw()
                for g in self.ghosts:
                    g.draw()
                if not self.play_state.is_action_pausing:
                    # transition to gameplay phase
                    self.sound.music_normal()
                    self.phase = 2
            elif self.phase == 2:
                if self.maze.remaining_pellets <= 0:
                    self.play_state.action_pause(120)
                    self.sound.stop_all()
                    self.phase = 3
                    continue
                if not self.play_state.is_action_pausing:
                    self.ghosts.update()
                    self.player.update()
                    self.collision_check()

                self.maze.draw()
                for g in self.ghosts:
                    g.draw()
                self.player.draw()
                self.scoreboard.update()
            elif self.phase == 3:
                # maze cleared, action pause
                self.maze.draw()
                for g in self.ghosts:
                    g.draw()
                self.player.draw()
                if not self.play_state.is_action_pausing:
                    self.phase = 4
                    self.play_state.action_pause(240)
                continue
            elif self.phase == 4:
                # clear message, action pause
                self.scoreboard.draw()
                self.maze.draw(draw_tiles=False)
                self.maze.blit_relative(self.clear_text, self.clear_text_rect)
                self.player.draw()
                if not self.play_state.is_action_pausing:
                    self.play_state.level += 1
                    self.reset(new_round=True)
            elif self.phase == 5:
                # game over
                self.scoreboard.draw()
                self.maze.draw()
                for g in self.ghosts: g.draw()
                self.maze.blit_relative(self.game_over_text, self.game_over_text_rect)
                if not self.play_state.is_action_pausing:
                    self.screen.fill((0, 0, 0))
                    return

            self.app.wait_next_frame()