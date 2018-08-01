from . import config as c
from . import sprites
import pygame as pg
import math

class Game_Object():
    def __init__(self, rect):
        self.rect = rect

    def __getattr__(self, name):
        """Makes code shorter by not having to type rect.pos when retrieving position"""
        if name == 'pos':
            return self.rect.pos
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        """Makes code shorter by not having to type rect.pos when setting position"""
        if name == 'pos':
            self.rect.pos = value
        else:
            object.__setattr__(self, name, value)
        
class Vector2():
    """Vector class for 2D positions and velocities"""
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y
    
    def __mul__(self, other):
        """Overload multiplication"""
        return Vector2(self.x * other, self.y * other)

    def __add__(self, other):
        """Overload Addition"""
        return Vector2(self.x + other.x, self.y + other.y)

class Rectangle():
    """Rectangle class for collider rectangles"""
    def __init__(self, pos = Vector2(), w = 0, h = 0):
        self.pos = pos
        self.w = w
        self.h = h

    def overlaps(self, other):
        """Check if two rectangles overlap"""
        return not(other.pos.x + other.w <= self.pos.x or 
                   other.pos.x >= self.pos.x + self.w or
                   other.pos.y + other.h <= self.pos.y or
                   other.pos.y >= self.pos.y + self.h)

    def check_collisions(self, collider_list):
        """Check collisions between two rectangles, if in a rangle of 100px"""
        for collider in collider_list:
            if abs(self.pos.x - collider.pos.x) < 100 or collider.rect.w >= 100: #Wider colliders are checked anyway
                if self.overlaps(collider.rect):
                    return collider

    def check_entity_collisions(self, entity_list):
        """Check collisions but return a list of all colliding entities"""
        others = []
        for entity in entity_list:
            if entity.rect is not self and abs(self.pos.x - entity.pos.x) < 100:
                if self.overlaps(entity.rect):
                    others.append(entity)
        return others
                

class Entity(Game_Object):
    """Entity class for Gameobjects that possess velocity"""
    def __init__(self, vel, rect):
        super(Entity, self).__init__(rect)
        self.vel = vel

class Camera(Rectangle):
    def __init__(self, pos, w, h):
        super(Camera, self).__init__(pos, w, h)
    
    def contains(self, other):
        return ((other.pos.x > self.pos.x and other.pos.x < self.pos.x + c.SCREEN_SIZE.x) or 
                (other.pos.x + other.w > self.pos.x and other.pos.x + other.w < self.pos.x + c.SCREEN_SIZE.x))

    def to_view_space(self, pos):
        """Returns position relative to camera"""
        return Vector2(pos.x - self.pos.x, pos.y)

    def update(self):
        """Update position of camera based on mario velocity and position"""
        if self.pos.x < c.MAXIMUM_CAMERA_SCROLL:
            if c.mario.pos.x > c.camera.pos.x + 300 and c.mario.vel.x > 0:
                c.camera.pos.x += c.mario.vel.x * c.delta_time

class State_Machine():
    """Manages states"""
    def __init__(self, initial_state, owner_object):
        self.state = initial_state
        self.owner_object = owner_object

    def on_event(self, event):
        """Updates current state and runs on_exit and on_enter"""
        prev_state = self.state
        new_state = self.state.on_event(event)
        if prev_state is not new_state:
            self.state.on_exit(self.owner_object)
            self.state = self.state.on_event(event)
            self.state.on_enter(self.owner_object, prev_state)

    def update(self):
        self.state.update(self.owner_object)

    def get_state(self):
        return self.state.__class__.__name__

class State():
    """State Class"""
    def on_event(self, event):
        """Handles events delegated to this state"""
        pass

    def on_enter(self, owner_object, prev_state):
        """Performs actions when entering state"""
        pass

    def update(self, owner_object):
        """Performs actions specific to state when active"""
        pass

    def on_exit(self, owner_object):
        """Performs actions when exiting state"""
        pass

class Digit_System():
    """Class for displaying and handling on-screen digits like score"""
    def __init__(self, start_pos, number_of_digits, start_value = 0):
        self.total_value = 0
        self.start_pos = start_pos
        self.number_of_digits = number_of_digits #Total amount of digits the digit system handles
        self.digit_array = []
        self.update_value(start_value)

    def update_value(self, new_value):
        """Updates the total value and digit array of the digit system"""
        self.digit_array = []
        self.total_value = new_value
        if new_value > 0:
            remaining_digits = self.number_of_digits - self.get_number_of_digits(new_value)
            for i in range(0, remaining_digits):
                self.digit_array.append(0)
            for x in str(self.total_value):
                self.digit_array.append(int(x))
        else:
            self.digit_array = [0] * self.number_of_digits
    
    def draw(self):
        """Draw the digit system"""
        for i, x in enumerate(self.digit_array):
            c.screen.blit(sprites.digits, (self.start_pos.x + 24 * i, self.start_pos.y), (24 * x, 0, 24, 21))

    def get_number_of_digits(self, value):
        """Gets the number of digits in an integer"""
        if value == 0:
            return 0
        elif value == 1:
            return 1
        else:
            return math.ceil(math.log10(value))

    
