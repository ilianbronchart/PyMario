from .. import config as c
from ..modules import Vector2, Entity, State, State_Machine, Rectangle
from .. import sprites
from .. import sounds
from ..utils import accelerate
from .. import level

class Goomba(Entity):
    def __init__(self, rect, vel):
        super(Goomba, self).__init__(vel, rect)
        self.animation = self.Animation()
        self.state_machine = State_Machine(self.Run_State(), self)
        self.vel.x = c.ENEMY_START_VEL_X

        self.is_active = False
        self.can_kill = True

    def draw(self):
        view_pos = c.camera.to_view_space(self.pos)
        if c.camera.contains(self.rect):
            c.screen.blit(sprites.tile_set, (view_pos.x, view_pos.y), self.animation.current_sprite)

    def update(self):
        self.state_machine.update()
        if self.is_active:
            if all(self.state_machine.get_state() != state for state in ['Squish_State', 'Dead_State']):
                accelerate(self, 0, c.GRAVITY)
                self.move()
        self.check_for_destroy()

    def check_for_destroy(self):
        if self.pos.y > c.SCREEN_SIZE.y:
            level.enemies.remove(self)

    def move(self):
        if self.vel.x != 0:
            self.move_single_axis(self.vel.x, 0)
        if self.vel.y != 0:
            self.move_single_axis(0, self.vel.y)

    def move_single_axis(self, dx, dy):
        self.pos.x += dx * c.delta_time
        self.pos.y += dy * c.delta_time
        if self.state_machine.get_state() != 'Knocked_State':
            self.check_collisions(dx, dy)

    def check_collisions(self, dx, dy):
        other_collider = self.rect.check_collisions(level.static_colliders + level.dynamic_colliders)
        other_enemy = self.rect.check_collisions([enemy for enemy in level.enemies if enemy is not self and enemy.is_active])

        if other_collider is None and other_enemy is None:
            return
        if other_collider is not None:
            if dx > 0:
                self.pos.x = other_collider.pos.x - self.rect.w
                self.vel.x = -self.vel.x
            elif dx < 0:
                self.pos.x = other_collider.pos.x + other_collider.rect.w
                self.vel.x = -self.vel.x
            elif dy > 0:
                self.pos.y = other_collider.pos.y - self.rect.h
                self.vel.y = 0
        if hasattr(other_collider, 'state_machine') and any(other_collider.state_machine.get_state() == state for state in ['Bounce_State', 'Break_State']):
            self.state_machine.on_event('knocked')
        if other_enemy is not None:
            self.pos.x -= dx * c.delta_time
            self.vel.x = -self.vel.x


    class Animation():
        def __init__(self):
            self.current_sprite = sprites.GOOMBA_RUN[0]

            self.anim_timer = c.INITIAL_TIMER_VALUE
            self.anim_frame = 0

            self.squish_delay_over = False

        def run_anim(self):
            self.current_sprite = sprites.GOOMBA_RUN[self.anim_frame % 2]
            self.anim_timer += c.delta_time
            if self.anim_timer > 14 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0

        def squish_delay(self):
            self.anim_timer += c.delta_time
            if self.anim_timer > 20 * c.delta_time:
                self.squish_delay_over = True

        def reset_anim_vars(self):
            self.anim_timer = 0
            self.anim_frame = 0

    class Run_State(State):
        def on_event(self, event):
            if event == 'knocked':
                return Goomba.Knocked_State()
            elif event == 'squish':
                return Goomba.Squish_State()
            return self

        def update(self, owner_object):
            owner_object.animation.run_anim()

        def on_exit(self, owner_object):
            owner_object.animation.reset_anim_vars()        

    class Knocked_State(State):
        def on_event(self, event):
            if event == 'dead':
                return Goomba.Dead_State()
            return self

        def on_enter(self, owner_object, prev_state):
            owner_object.vel.y = c.GOOMBA_KNOCKED_VEL_Y
            owner_object.animation.current_sprite = sprites.GOOMBA_KNOCKED
            sounds.kick.play()
            c.killed_goombas += 1

    class Squish_State(State):
        def on_event(self, event):
            if event == 'dead':
                return Goomba.Dead_State()
            return self
    
        def on_enter(self, owner_object, prev_state):
            owner_object.animation.current_sprite = sprites.GOOMBA_SQUISHED
            owner_object.rect = Rectangle(owner_object.pos, 0, 0)
            sounds.stomp.play()
            c.killed_goombas += 1

        def update(self, owner_object):
            owner_object.animation.squish_delay()
            if owner_object.animation.squish_delay_over:
                owner_object.state_machine.on_event('dead')

    class Dead_State(State):
        def on_enter(self, owner_object, prev_state):
            level.enemies.remove(owner_object)

class Turtle(Entity):
    def __init__(self, rect, vel):
        super(Turtle, self).__init__(vel, rect)
        self.animation = self.Animation()
        self.state_machine = State_Machine(self.Run_State(), self)
        self.vel.x = c.ENEMY_START_VEL_X
        self.is_active = False

        self.can_kill = True

    def update(self):
        if self.is_active:
            accelerate(self, 0, c.GRAVITY)
            self.move()
            self.state_machine.update()
        self.check_for_destroy()

    def draw(self):
        view_pos = c.camera.to_view_space(self.pos)
        if c.camera.contains(self.rect):
            c.screen.blit(sprites.tile_set, (view_pos.x, view_pos.y), self.animation.current_sprite)
    
    def check_for_destroy(self):
        if self.pos.y > c.SCREEN_SIZE.y:
            level.enemies.remove(self)
    
    def move(self):
        if self.vel.x != 0:
            self.move_single_axis(self.vel.x, 0)
        if self.vel.y != 0:
            self.move_single_axis(0, self.vel.y)

    def move_single_axis(self, dx, dy):
        self.pos.x += dx * c.delta_time
        self.pos.y += dy * c.delta_time
        if self.state_machine.get_state() != 'Knocked_State':
            self.check_collisions(dx, dy)

    def check_collisions(self, dx, dy):
        other_collider = self.rect.check_collisions(level.static_colliders + level.dynamic_colliders)
        other_enemy = self.rect.check_collisions([enemy for enemy in level.enemies if enemy is not self])

        if other_collider is None and other_enemy is None:
            return
        if other_collider is not None:
            if dx > 0:
                self.pos.x = other_collider.pos.x - self.rect.w
                self.vel.x = -self.vel.x
            elif dx < 0:
                self.pos.x = other_collider.pos.x + other_collider.rect.w
                self.vel.x = -self.vel.x
            elif dy > 0:
                self.pos.y = other_collider.pos.y - self.rect.h
                self.vel.y = 0

        if other_enemy is not None:
            if self.state_machine.get_state() != 'Move_Shell':
                self.pos.x -= dx * c.delta_time
                self.vel.x = -self.vel.x
            else:
                other_enemy.state_machine.on_event('knocked')
                other_enemy.is_active = True

    class Animation():
        def __init__(self):
            self.current_sprite = sprites.TURTLE[0]

            self.anim_timer = 0
            self.anim_frame = 0

        def run_anim(self):
            self.current_sprite = sprites.TURTLE[self.anim_frame % 2]
            self.anim_timer += c.delta_time
            if self.anim_timer > 13 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0

    class Run_State(State):
        def on_event(self, event):
            if event == 'squish':
                return Turtle.Shell_State()
            return self

        def update(self, owner_object):
            owner_object.animation.run_anim()

    class Shell_State(State):
        def on_event(self, event):
            if event == 'move shell':
                return Turtle.Move_Shell()
            return self

        def on_enter(self, owner_object, prev_state):
            owner_object.rect.h = 42
            owner_object.pos.y += 30
            owner_object.animation.current_sprite = sprites.TURTLE_SHELL
            owner_object.vel.x = 0
            owner_object.can_kill = False
            sounds.stomp.play()

    class Move_Shell(State):
        def __init__(self):
            self.can_kill_timer = 0

        def on_event(self, event):
            return self

        def on_enter(self, owner_object, prev_state):
            sounds.kick.play()

        def update(self, owner_object):
            self.can_kill_timer += c.delta_time
            if self.can_kill_timer > 10 * c.delta_time:
                owner_object.can_kill = True
