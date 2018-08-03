from . import config as c
from .basetypes import Vector2
import math

def clamp(x, a, b):
    """Clamps value x between a and b"""
    return max(a, min(b, x))

def accelerate(obj, accel_x, accel_y, limit_x = None):
    """Accelerate until limit is reached"""
    obj.vel += Vector2(accel_x, accel_y) * c.delta_time
    if limit_x != None:
        if obj.vel.x > 0:
            obj.vel.x = clamp(obj.vel.x, 0, limit_x)
        elif obj.vel.x < 0:
            obj.vel.x = clamp(obj.vel.x, -limit_x, 0)

def get_flipped_sprite(sprite):
    """Returns coordinates of a flipped sprite"""
    #429 is the width of the atlas
    return (429 - sprite[0] - sprite[2], sprite[1], sprite[2], sprite[3])