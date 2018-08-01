from .modules import Vector2
from . import config as c
from . import sprites
import pygame as pg

class Menu():
    def __init__(self):
        self.selected = 0
        self.quit_state = None

        self.pressed_up = False
        self.pressed_down = False

        self.selector_pos = Vector2(239, 404)

    def draw(self):
        c.screen.fill((0, 0, 0))
        c.screen.blit(sprites.menu, (0, 0))
        c.screen.blit(sprites.tile_set, (self.selector_pos.x, self.selector_pos.y), sprites.SELECTOR)

    def check_for_quit(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit_state = 'exit'
                return False

        if c.keys[pg.K_ESCAPE]:
            self.quit_state = 'exit'
            return False

        if c.keys[pg.K_RETURN] and self.selected % 2 == 0:
            self.quit_state = 'play'
            return False
        
        if c.keys[pg.K_w] and not self.pressed_down and not self.pressed_up:
            self.selected += 1
            self.pressed_up = True
        if c.keys[pg.K_s] and not self.pressed_up and not self.pressed_down:
            self.selected -= 1
            self.pressed_down = True

        if not c.keys[pg.K_w]:
            self.pressed_up = False
        if not c.keys[pg.K_s]:
            self.pressed_down = False

        return True

    def menu_loop(self):
        while True:
            c.keys = pg.key.get_pressed()
            c.clock.tick()

            if self.selected % 2 == 0:
                self.selector_pos = Vector2(239, 404)
            else:
                self.selector_pos = Vector2(239, 448)
            self.draw()

            if not self.check_for_quit():
                break

            pg.display.flip()

            