from ..modules import Game_Object, Vector2, Entity
from .. import config as c
from .. import sprites
from .. import sounds
from .. import level
from ..utils import accelerate

class Coin(Game_Object):
    """Coin item class"""
    def __init__(self, rect):
        super(Coin, self).__init__(rect)
        self.animation = self.Animation(self.pos.y)
        self.deployed = False
        self.collected = False

    def update(self):
        self.animation.anim()
        self.pos.y = self.animation.new_y
        if self.animation.bounce_iteration > 23:
            self.collected = True

        self.check_for_destroy()

    def check_for_destroy(self):
        """Checks if instance can be destroyed"""
        if self.collected:
            level.items.remove(self)

    def draw(self):
        view_pos = c.camera.to_view_space(self.pos)
        c.screen.blit(sprites.tile_set, (view_pos.x, view_pos.y), self.animation.current_sprite)

    class Animation():
        """Contains specific animation variables and functions for this class"""
        def __init__(self, start_height):
            self.current_sprite = sprites.COIN[0]

            self.start_height = start_height
            self.new_y = start_height
            self.anim_timer = c.INITIAL_TIMER_VALUE
            self.anim_frame = 0
            self.bounce_iteration = 0

        def anim(self):
            """Spinning animation"""
            self.current_sprite = sprites.COIN[self.anim_frame % 4]
            self.anim_timer += c.delta_time
            if self.anim_timer > 3 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0
            self.bounce_iteration += 0.6

            self.new_y = self.start_height - self.anim_function(self.bounce_iteration)

        def anim_function(self, bounce_iteration):
            """Returns new y based on quadratic function to create bounce"""
            return -(bounce_iteration - 12) ** 2 + 144

class Super_Mushroom(Entity):
    """Super mushroom class"""
    def __init__(self, rect, vel):
        super(Super_Mushroom, self).__init__(vel, rect)

        self.deployed = False
        self.collected = False

        self.animation = self.Animation(self.pos.y)

    def draw(self):
        view_pos = c.camera.to_view_space(self.pos)
        c.screen.blit(sprites.tile_set, (view_pos.x, view_pos.y), sprites.SUPER_MUSHROOM)

    def update(self):
        if self.animation.has_animated:
            accelerate(self, 0, c.GRAVITY)
            self.move()
        else:
            self.animation.deploy_anim()
            self.pos.y = self.animation.new_y

        self.check_for_destroy()

    def check_for_destroy(self):
        """Checks if instance can be destroyed"""
        if self.collected:
            sounds.powerup.play()
            c.collected_mushrooms += 1
            level.items.remove(self)

    def move(self):
        """Separates x and y movement"""
        if self.vel.x != 0:
            self.move_single_axis(self.vel.x, 0)
        if self.vel.y != 0:
            self.move_single_axis(0, self.vel.y)

    def move_single_axis(self, dx, dy):
        """Checks to see whether x or y movement caused collisions"""
        self.pos.x += dx * c.delta_time
        self.pos.y += dy * c.delta_time
        other_collider = self.rect.check_collisions(level.static_colliders + level.dynamic_colliders)

        if other_collider is None:
            return
        if dx > 0:
            self.pos.x = other_collider.pos.x - self.rect.w
            self.vel.x = -self.vel.x
        elif dx < 0:
            self.pos.x = other_collider.pos.x + other_collider.rect.w
            self.vel.x = -self.vel.x
        elif dy > 0:
            self.pos.y = other_collider.pos.y - self.rect.h
            self.vel.y = 0
        
    class Animation():
        """Contains specific animation variables and functions for this class"""
        def __init__(self, start_height):
            self.new_y = start_height
            self.anim_iteration = 0
            self.has_animated = False

        def deploy_anim(self):
            """Animation when deploying super mushroom"""
            if self.anim_iteration == 48:
                self.has_animated = True
            if not self.has_animated:
                self.new_y -= 1
                self.anim_iteration += 1 
