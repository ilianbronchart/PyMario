from .basetypes import Vector2
import pygame as pg

#Variables shared among different basetypes
screen = None
clock = None
camera = None
keys = None
delta_time = None
mario = None
final_count_down = False

#Colors for level loading
BLACK = (0, 0, 0, 255)
RED = (255, 0, 0, 255)
GRAY = (100, 100, 100, 255)
YELLOW = (255, 255, 0, 255)
GREEN = (100, 255, 100, 255)
BROWN = (124, 66, 0, 255)
PURPLE = (124, 0, 255, 255)

#Background color of level
BACKGROUND_COLOR = (107, 140, 255)

#Window settings
SCREEN_SIZE = Vector2(744, 672)
CAPTION = 'Mario Bros'

#Start positions
MARIO_START_POSITION = Vector2(138, 552)
FOREGROUND_POS = Vector2(9840, 505)

TILE_SIZE = 48

#Physics values
ACCELERATION = 0
MARIO_ACCELERATION = 0.0005
MAX_VEL = 0.35
GRAVITY = 0.002
MAX_JUMP_HEIGHT = 140
FRICTION = 1
DECEL_FRICTION = 0.95
BRAKE_FRICTION = 0.85

#Velocities for different events
BOUNCE_VEL = 0.1
JUMP_VELOCITY = -0.5
MUSHROOM_START_VEL_X = 0.2
ENEMY_START_VEL_X = -0.1
STOMP_VEL = -0.4
DEATH_VEL_Y = -0.8
GOOMBA_KNOCKED_VEL_Y = -0.8

#End of level settings
MAXIMUM_CAMERA_SCROLL = 9300
LEVEL_END_X = 9840

#Distance from left side of the screen, when camera starts following
CAMERA_FOLLOW_X = 300

#Sets timer value so animations start instantly instead of counting up first
INITIAL_TIMER_VALUE = 1000

#Score values
collected_coins = 0
total_score = 0
COIN_SCORE = 200
MUSHROOM_SCORE = 1000
GOOMBA_SCORE = 100
TIME_SCORE = 1000

#Events when certain songs end
WIN_SONG_END = pg.USEREVENT + 1
DEATH_SONG_END = pg.USEREVENT + 2
OUT_OF_TIME_END = pg.USEREVENT + 3









