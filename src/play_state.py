import pygame as pg

import ghost as gh

class PGStopwatch:
    """A stopwatch that uses PyGame's timing functions."""
    def __init__(self):
        self.reset()

    def reset(self, restart=False):
        self._base = None
        self._pause_delta = None
        self.started = False
        self.paused = False

        if restart: self.start()
    
    def start(self):
        if self.started:
            self.resume()
        else:
            self._base = pg.time.get_ticks()
            self.started = True
    
    def pause(self):
        self._pause_delta = self.elapsed()
        self.paused = True
    
    def resume(self):
        if self.started and self.paused:
            self.paused = False
            self._base = pg.time.get_ticks() - self._pause_delta

    def elapsed(self):
        if not self.started: return -1
        if self.paused:
            return self._pause_delta
        else:
            return pg.time.get_ticks() - self._base

    

class PlayState:
    MODE_TIMER = {
        gh.GhostMode.SCATTER: 420,
        gh.GhostMode.CHASE: 1200,
        gh.GhostMode.FRIGHTENED: 700
    }

    MODE_NATURAL_NEXT = {
        gh.GhostMode.SCATTER: gh.GhostMode.CHASE,
        gh.GhostMode.CHASE: gh.GhostMode.SCATTER
    }
    """Frames remaining until mode ends. Should tick down every frame (1/60 of a second)."""

    def __init__(self, play):
        self.sw = PGStopwatch()
        self.play = play

        # Tile coordinates for our portals
        self.portal_a = None
        self.portal_b = None

        self.level = 0
        """How many times the player has cleared the maze."""

        self.is_action_pausing = False
        """Game will not be player-pausable; this is more for effect."""

        self.pause_timer = 0
        """How much time to keep the game paused (in frames)."""

        self.is_frightened = False
        """Whether we are in frightened mode or not."""

        self.frightened_timer = PlayState.MODE_TIMER[gh.GhostMode.FRIGHTENED]
        """Frames remaining in frightened mode. Starts at 600."""

        self.mode_ghosts = gh.GhostMode.SCATTER
        '''Mode the ghosts should preferably stay at.
        
        Possible values:
        0: Scatter
        1: Chase'''

        self.mode_countdown = PlayState.MODE_TIMER[self.mode_ghosts]
        """Frames remaining until mode ends. Should tick down every frame (1/60 of a second)."""

        self.hide_ghosts = False
        """For animation purposes; hides ghosts."""
        
        self.hide_player = False
        """For animation purposes; hides player."""

        self.reset_after_death()
    
    def reset(self):
        self.hide_ghosts = False
        self.hide_player = False
        self.frightened_timer = PlayState.MODE_TIMER[gh.GhostMode.FRIGHTENED]
        self.is_frightened = False
        self.mode_ghosts = gh.GhostMode.SCATTER
        self.mode_countdown = PlayState.MODE_TIMER[self.mode_ghosts]

    def action_pause(self, frames):
        self.pause_timer = frames
        self.is_action_pausing = True

    def power_pellet_eatened(self):
        self.is_frightened = True
        self.frightened_timer = PlayState.MODE_TIMER[gh.GhostMode.FRIGHTENED]
    
    

    def reset_after_death(self):
        self.portal_a = None
        self.portal_b = None
        self.mode_ghosts = gh.GhostMode.SCATTER
        self.mode_countdown = PlayState.MODE_TIMER[self.mode_ghosts]

    def update_ghost_mode(self):
        if self.is_frightened:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.frightened_timer = PlayState.MODE_TIMER[gh.GhostMode.FRIGHTENED]
                self.is_frightened = False
                self.play.set_ghosts_mode(self.mode_ghosts)
                self.play.sound.music_normal()
        else:
            self.mode_countdown -= 1
            if self.mode_countdown <= 0:
                self.mode_ghosts = PlayState.MODE_NATURAL_NEXT[self.mode_ghosts]
                self.mode_countdown = PlayState.MODE_TIMER[self.mode_ghosts]
                self.play.set_ghosts_mode(self.mode_ghosts)

    def update_action_pause(self):
        if self.pause_timer > 0: self.pause_timer -= 1
        self.is_action_pausing = self.pause_timer > 0

    def update(self):
        self.update_action_pause()
        if self.is_action_pausing: return
        
        self.update_ghost_mode()