from .sprites import level_1
from .basetypes import Vector2, Rectangle
from . import config as c
from .components.tiles import Question, Brick, Collider_Rect, Flagpole
from .components.items import *
from .components.enemies import *

#Colliders that don't possess velocity
static_colliders = []

#Colliders that possess velocity
dynamic_colliders = []

coins = []
super_mushrooms = []
enemies = []

#Fragments go here when a brick tile gets broken
brick_fragments = []

#Start and End tile for grouping large rows of tiles into one collider
start_tile = None
end_tile = None

#Read pixel data from level map and instantiate objects corresponding to pixel colors
for y in range(0, level_1.size[1]):
    for x in range(0, level_1.size[0]):

        color = level_1.getpixel((x, y))
        pos = Vector2(x * c.TILE_SIZE, y * c.TILE_SIZE + 24)

        #Black = Static ground collider, which are grouped together for optimizations
        if color == c.BLACK:
            if start_tile == None:
                start_tile = pos
            if end_tile == None:
                if x + 1 > level_1.size[0]:
                    end_tile = pos
                if level_1.getpixel((x + 1, y)) != c.BLACK:
                    end_tile = pos
            if end_tile != None and start_tile != None:
                w = end_tile.x - start_tile.x + c.TILE_SIZE
                h = c.TILE_SIZE
                rect = Rectangle(start_tile, w, h)
                static_colliders.append(Collider_Rect(rect))
                end_tile = None
                start_tile = None
        
        #Red = Pipe collider
        elif color == c.RED:
            h = c.SCREEN_SIZE.y - pos.y
            w = 2 * c.TILE_SIZE
            rect = Rectangle(pos, w, h)
            static_colliders.append(Collider_Rect(rect))

        #Yellow = Question tile with coin as item
        elif color == c.YELLOW:
            coin_rect = Rectangle(Vector2(pos.x, pos.y), 48, 42)
            contents = Coin(coin_rect)
            coins.append(contents)
            rect = Rectangle(pos, c.TILE_SIZE, c.TILE_SIZE)
            dynamic_colliders.append(Question(rect, contents))

        #Gray = Brick tile
        elif color == c.GRAY:
            rect = Rectangle(pos, c.TILE_SIZE, c.TILE_SIZE)
            dynamic_colliders.append(Brick(rect))

        #Green = Question tile with mushroom as item
        elif color == c.GREEN:
            mushroom_rect = Rectangle(Vector2(pos.x, pos.y), c.TILE_SIZE, c.TILE_SIZE)
            contents = Super_Mushroom(mushroom_rect, Vector2(c.MUSHROOM_START_VEL_X, 0))
            super_mushrooms.append(contents)
            rect = Rectangle(pos, c.TILE_SIZE, c.TILE_SIZE)
            dynamic_colliders.append(Question(rect, contents))

        #Brown = Goomba
        elif color == c.BROWN:
            rect = Rectangle(pos, c.TILE_SIZE, c.TILE_SIZE)
            enemies.append(Goomba(rect, Vector2()))

        elif color == c.PURPLE:
            rect = Rectangle(Vector2(pos.x, pos.y - 24), 48, 72)
            enemies.append(Turtle(rect, Vector2()))

#Instantiate flagpole
rect = Rectangle(Vector2(9504, 96), 48, 456)
flag_pos = Vector2(9480, 120)
c.flagpole = Flagpole(rect, flag_pos)

