from . import config as c
from . import level
from . import sprites
from . import sounds
from .modules import Camera, Vector2, Rectangle, Digit_System
import pygame as pg
from .components import mario

class Main():
    def __init__(self):
        c.camera = Camera(Vector2(), c.SCREEN_SIZE.x, c.SCREEN_SIZE.y)
        c.mario = mario.Mario(Rectangle(c.MARIO_START_POSITION, 36, 48))

        pg.mixer.music.load(sounds.main_theme)
        pg.mixer.music.play()

        self.quit_state = None
        self.out_of_time = False
        self.played_coin_sound = False

        self.score_system = Digit_System(Vector2(66, 49), 6)
        self.coin_score = Digit_System(Vector2(306, 49), 2)
        self.time = Digit_System(Vector2(610, 49), 3, 300)
        self.timer = 0

    def draw(self):
        c.screen.fill(c.BACKGROUND_COLOR)
        self.draw_background()
        
        for item in level.items:
            if item.deployed:
                item.draw()

        for tile in level.dynamic_colliders:
            if c.camera.contains(tile.rect):
                view_pos = c.camera.to_view_space(tile.pos)
                tile.draw(view_pos)

        for enemy in level.enemies:
            if enemy.is_active:
                enemy.draw()

        for fragment in level.brick_fragments:
            fragment.draw()

        c.flagpole.draw_flag()

        c.mario.draw()

        self.draw_foreground()
        self.draw_digit_systems()

    def draw_background(self):
        c.screen.blit(sprites.background, 
                      (0, 0), 
                      (c.camera.pos.x, c.camera.pos.y, c.SCREEN_SIZE.x, c.SCREEN_SIZE.y))

    def draw_foreground(self):
        view_pos = c.camera.to_view_space(c.FOREGROUND_POS)
        if view_pos.x < c.camera.pos.x + c.SCREEN_SIZE.x:
            c.screen.blit(sprites.foreground, (view_pos.x, view_pos.y))
        c.screen.blit(sprites.text_image, (0,0))

    def handle_digit_systems(self):
        if not c.mario.current_mario_state == 'Dead_Mario':
            c.total_score = (c.collected_coins * c.COIN_SCORE +
                            c.collected_mushrooms * c.MUSHROOM_SCORE+
                            c.killed_goombas * c.GOOMBA_SCORE +
                            c.time_score * c.TIME_SCORE)

            self.handle_time()
            self.score_system.update_value(c.total_score)
            self.coin_score.update_value(c.collected_coins)

    def handle_time(self):
        self.timer += c.delta_time
        if not c.final_count_down and self.timer > 14 * c.delta_time:
            self.time.update_value(self.time.total_value - 1)
            self.timer = 0

        if not c.mario.current_mario_state == 'Win_State':
            if not c.final_count_down and self.time.total_value < 100 and not self.out_of_time:
                pg.mixer.music.stop()
                pg.mixer.music.set_endevent(c.OUT_OF_TIME_END)
                pg.mixer.music.load(sounds.out_of_time)
                pg.mixer.music.play()
                self.out_of_time = True

        if not c.final_count_down and self.time.total_value == 0:
            c.mario.mario_states.on_event('dead')


        if c.final_count_down and self.time.total_value > 0:
            self.time.update_value(self.time.total_value - 1)
            c.time_score += 1
            sounds.count_down.play()
            if self.time.total_value == 0:
                sounds.count_down.stop()
                sounds.coin.play()

    def draw_digit_systems(self):
        self.score_system.draw()
        self.coin_score.draw()
        self.time.draw()

    def update_level(self):
        c.mario.update()
        c.mario.physics_update()
        c.camera.update()
        for tile in level.dynamic_colliders:
            tile.update()

        for item in level.items:
            if item.deployed:
                item.update()

        if not c.mario.freeze_movement:
            for enemy in level.enemies:
                if enemy.pos.x < c.camera.pos.x + c.SCREEN_SIZE.x:
                    enemy.is_active = True
                enemy.update()

        for fragment in level.brick_fragments:
            fragment.update()

        c.flagpole.update()

    def check_for_quit(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            
            if event.type == c.WIN_SONG_END and self.time.total_value == 0:
                self.quit_state = 'menu'
                return False

            if event.type == c.DEATH_SONG_END:
                self.quit_state = 'menu'
                return False

            if event.type == c.OUT_OF_TIME_END:
                pg.mixer.music.stop()
                pg.mixer.music.load(sounds.main_theme_sped_up)
                pg.mixer.music.play()

        if c.mario.to_menu:
            self.quit_state = 'menu'
            return False

        if c.keys[pg.K_ESCAPE]:
            return False
        return True

    def main_loop(self):
        while True:
            c.delta_time = c.clock.tick(60)
            c.keys = pg.key.get_pressed()

            self.update_level()
            self.handle_digit_systems()
            self.draw()

            if not self.check_for_quit():
                break

            pg.display.update()