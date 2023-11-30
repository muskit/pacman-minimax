import sys
import pygame as pg

def process_events(play):
    player = play.player
    for ev in pg.event.get():
        if ev.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif ev.type == pg.KEYDOWN:
            pass
        
    player_input(player)
            

def player_input(player):
    keys = pg.key.get_pressed() # currently held keys
    if keys[pg.K_RIGHT]:
        player.try_set_direction('right')
    if keys[pg.K_LEFT]:
        player.try_set_direction('left')
    if keys[pg.K_DOWN]:
        player.try_set_direction('down')
    if keys[pg.K_UP]:
        player.try_set_direction('up')