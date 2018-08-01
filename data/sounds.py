import pygame as pg
from os import path

pg.init()
#initialize mixer
pg.mixer.pre_init(44100, 16, 2, 4096)

sounds_folder = path.join(path.dirname(__file__), 'resources', 'sounds')

#Load all sounds
small_jump = pg.mixer.Sound(path.join(sounds_folder, 'small_jump.ogg'))
big_jump = pg.mixer.Sound(path.join(sounds_folder, 'big_jump.ogg'))
bump = pg.mixer.Sound(path.join(sounds_folder, 'bump.ogg'))
powerup_appears = pg.mixer.Sound(path.join(sounds_folder, 'powerup_appears.ogg'))
powerup = pg.mixer.Sound(path.join(sounds_folder, 'powerup.ogg'))
coin = pg.mixer.Sound(path.join(sounds_folder, 'coin.ogg'))
stomp = pg.mixer.Sound(path.join(sounds_folder, 'stomp.ogg'))
brick_smash = pg.mixer.Sound(path.join(sounds_folder, 'brick_smash.ogg'))
kick = pg.mixer.Sound(path.join(sounds_folder, 'kick.ogg'))
flagpole_sound = pg.mixer.Sound(path.join(sounds_folder, 'flagpole.wav'))
count_down = pg.mixer.Sound(path.join(sounds_folder, 'count_down.ogg'))
pipe = pg.mixer.Sound(path.join(sounds_folder, 'pipe.ogg'))

#Get path to music files
main_theme = path.join(sounds_folder, 'main_theme.ogg')
stage_clear = path.join(sounds_folder, 'stage_clear.wav')
death = path.join(sounds_folder, 'death.wav')
out_of_time = path.join(sounds_folder, 'out_of_time.wav')
main_theme_sped_up = path.join(sounds_folder, 'main_theme_sped_up.ogg')
