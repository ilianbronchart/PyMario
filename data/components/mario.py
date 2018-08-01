from ..modules import Game_Object, Vector2, Entity, Rectangle, State_Machine, State
from .. import config as c
from .. import sprites
from .. import sounds
from ..utils import accelerate, clamp, get_flipped_sprite
from .. import level
import pygame as pg
import random

class Mario(Entity):
    def __init__(self, rect, vel = Vector2()):
        super(Mario, self).__init__(vel, rect)
        self.animation = self.Animation()
        self.action_states = State_Machine(self.Idle_State(), self)
        self.mario_states = State_Machine(self.Small_Mario(), self)

        self.pressed_left = False
        self.pressed_right = False
        self.spacebar = False
        self.crouch = False
        self.flip_sprites = False
        self.freeze_movement = False
        self.freeze_input = False
        self.to_menu = False

        self.start_height = 0

    def __getattr__(self, name):
        if name == 'current_action_state':
            return self.action_states.get_state()
        elif name == 'pos':
            return self.rect.pos
        elif name == 'current_mario_state':
            return self.mario_states.get_state()
        return object.__getattribute__(self, name)

    def draw(self):
        if c.camera.contains(self.rect):
            view_pos = c.camera.to_view_space(self.pos)
            if self.flip_sprites:
                flipped_sprite = get_flipped_sprite(self.animation.current_sprite)
                c.screen.blit(sprites.tile_set_flipped, (view_pos.x, view_pos.y), flipped_sprite)
            else:
                c.screen.blit(sprites.tile_set, (view_pos.x, view_pos.y), self.animation.current_sprite)

    def update(self):
        if not self.freeze_input:
            if c.keys[pg.K_a] and not c.keys[pg.K_d]:
                self.pressed_left = True
                c.ACCELERATION = -c.MARIO_ACCELERATION
            elif c.keys[pg.K_d] and not c.keys[pg.K_a]:
                self.pressed_right = True
                c.ACCELERATION = c.MARIO_ACCELERATION
            else:
                c.ACCELERATION = 0
            
            if not c.keys[pg.K_a]:
                self.pressed_left = False
            if not c.keys[pg.K_d]:
                self.pressed_right = False

            if c.keys[pg.K_SPACE] and not self.spacebar:
                self.spacebar = True
                self.action_states.on_event('jump')
            
            if not c.keys[pg.K_SPACE]:
                self.spacebar = False

            if c.keys[pg.K_s]:
                self.crouch = True
            else:
                self.crouch = False

    def physics_update(self):
        if not self.current_mario_state == 'Invincible_State':
            self.mario_states.update()
        if not self.freeze_movement:
            self.state_events()
            self.action_states.update()
            self.movement()
            if self.pos.y > self.start_height:
                self.action_states.on_event('no jump')
            self.check_flip_sprites()

        if self.current_mario_state == 'Invincible_State':
            self.mario_states.update()

        self.rect.h = self.animation.current_sprite[3]

        if self.pos.y > c.SCREEN_SIZE.y:
            self.mario_states.on_event('dead')

    def movement(self):
        accelerate(self, c.ACCELERATION, c.GRAVITY, c.MAX_VEL)
        self.vel.x *= c.FRICTION
        self.move()

    def check_flip_sprites(self):
        if self.vel.x < 0:
                self.flip_sprites = True
        elif self.vel.x > 0:
            self.flip_sprites = False

    def state_events(self):
        if any(self.current_action_state == state for state in ['Move_State', 'Decel_State', 'Brake_State', 'Idle_State']):
            self.start_height = self.pos.y

        if self.vel.y == 0:
            if self.pressed_left or self.pressed_right:
                self.action_states.on_event('move')

            if ((self.vel.x < 0 and not self.pressed_left) or
                (self.vel.x > 0 and not self.pressed_right)):
                self.action_states.on_event('decel')
            
            if ((self.vel.x < 0 and self.pressed_right) or
                (self.vel.x > 0 and self.pressed_left)):
                self.action_states.on_event('brake')

            if abs(self.vel.x) < 0.02 and self.current_action_state != 'Move_State':
                self.vel.x = 0
                self.action_states.on_event('idle')

        if all(self.current_action_state != state for state in ['Decel_State', 'Brake_State', 'Crouch_State']):
            c.FRICTION = 1

        if any(self.current_action_state == state for state in ['Jump_State', 'No_Jump_State']):
            if self.animation.mario_size == 'Small_Mario':
                self.animation.current_sprite = sprites.SMALL_MARIO_JUMP
            else:
                self.animation.current_sprite = sprites.BIG_MARIO_JUMP

        if self.current_mario_state == 'Big_Mario':
            if self.crouch:
                self.action_states.on_event('crouch')

    def move(self):
        if self.vel.x != 0:
            self.move_single_axis(self.vel.x, 0)
        if self.vel.y != 0:
            self.move_single_axis(0, self.vel.y)

    def move_single_axis(self, dx, dy):
        self.pos.x += dx * c.delta_time
        self.pos.y += dy * c.delta_time

        self.collider_collisions(dx, dy)
        if self.current_mario_state != 'Invincible_State':
            self.check_entity_collisions() 

        self.check_backtrack()

    def check_backtrack(self):
        if self.pos.x < c.camera.pos.x:
            self.pos.x = clamp(self.pos.x, c.camera.pos.x, c.SCREEN_SIZE.x)
            self.vel.x = 0    
            self.action_states.on_event('idle')      

    def collider_collisions(self, dx, dy):
        other_collider = self.rect.check_collisions(level.static_colliders + level.dynamic_colliders)

        if other_collider is None:
            return
        if dx > 0:
            if self.current_action_state == 'Move_State':
                self.action_states.on_event('idle')
            self.pos.x = other_collider.pos.x - self.rect.w
            self.vel.x = 0
        elif dx < 0:
            if self.current_action_state == 'Move_State':
                self.action_states.on_event('idle')
            self.pos.x = other_collider.pos.x + other_collider.rect.w
            self.vel.x = 0
        elif dy > 0:
            self.pos.y = other_collider.pos.y - self.rect.h
            self.vel.y = 0
            if self.current_action_state == 'No_Jump_State':
                self.action_states.on_event('idle')
        elif dy < 0:
            self.interact_with_tile(other_collider)
            self.action_states.on_event('no jump')
            self.pos.y = other_collider.pos.y + other_collider.rect.h
            self.vel.y = c.BOUNCE_VEL

    def check_entity_collisions(self):
        entities = self.rect.check_entity_collisions(level.super_mushrooms + level.enemies)

        for entity in entities:
            if entity.__class__.__name__ == 'Super_Mushroom' and entity.deployed:
                self.mario_states.on_event('grow')
                entity.collected = True

            if hasattr(entity, 'state_machine') and entity.state_machine.get_state() != 'Knocked_State':
                if entity.state_machine.get_state() == 'Shell_State':
                    if self.pos.x + self.rect.w < entity.pos.x + entity.rect.w / 2:
                        entity.vel.x = 0.5
                    elif self.pos.x + self.rect.w > entity.pos.x + entity.rect.w / 2:
                        entity.vel.x = -0.5
                    elif self.vel.x < 0:
                        entity.vel.x = -0.5
                    elif self.vel.x > 0:
                        entity.vel.x = 0.5
                    else:
                        entity.vel.x = random.choice([-0.5, 0.5])
                    entity.state_machine.on_event('move shell')

                elif self.pos.y + self.rect.h - self.vel.y * c.delta_time < entity.pos.y:
                    if entity.state_machine.get_state() == 'Run_State':
                        self.vel.y = c.STOMP_VEL
                        self.pos.y = entity.pos.y - self.rect.h
                        entity.state_machine.on_event('squish')
                        return
                else:
                    if entity.state_machine.get_state() != 'Shell_State' and entity.can_kill:
                        self.mario_states.on_event('shrink')

    def interact_with_tile(self, tile):
        if self.current_mario_state == 'Small_Mario':
            tile.state_machine.on_event('bounce')
            if tile.__class__.__name__ == 'Brick':
                sounds.bump.play()
        elif self.current_mario_state == 'Big_Mario':
            tile.state_machine.on_event('break')
            if tile.__class__.__name__ == 'Question':
                tile.state_machine.on_event('bounce')

    class Animation():
        def __init__(self):
            self.current_sprite = sprites.SMALL_MARIO_IDLE

            self.mario_size = 'Small_Mario'
            self.anim_frame = 0
            self.anim_timer = c.INITIAL_TIMER_VALUE
            self.invincible_timer = 0

            self.start_height = None
            self.new_y = self.start_height

            self.grow_frames = [0, 1, 0, 1, 2, 0, 1, 2]
            self.shrink_frames = [0, 1, 0, 1, 2, 1, 2, 1]
            self.run_frames = [0, 1, 2, 1]
            self.start_sprite_height = 0

        def reset_anim_vars(self):
            self.anim_frame = 0
            self.anim_timer = c.INITIAL_TIMER_VALUE

        def grow_anim(self):
            self.current_sprite = sprites.GROW_SPRITES[self.grow_frames[self.anim_frame]]
            self.anim_timer += c.delta_time
            if self.anim_timer > 6 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0
            self.new_y = self.start_height - (self.current_sprite[3] - 48)

        def run_anim(self):
            if self.mario_size == 'Small_Mario':
                self.current_sprite = sprites.SMALL_MARIO_RUN[self.run_frames[self.anim_frame % 4]]
            else:
                self.current_sprite = sprites.BIG_MARIO_RUN[self.run_frames[self.anim_frame % 4]]
            self.anim_timer += c.delta_time
            if self.anim_timer > 6 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0

        def shrink_anim(self):
            self.current_sprite = sprites.SHRINK_SPRITES[self.shrink_frames[self.anim_frame]]
            self.anim_timer += c.delta_time
            if self.anim_timer > 6 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0
            self.new_y = self.start_height + (self.start_sprite_height - self.current_sprite[3])

        def win_anim_on_flag(self):
            if self.mario_size == 'Small_Mario':
                self.current_sprite = sprites.WIN_SPRITES_SMALL[self.anim_frame % 2]
            else:
                self.current_sprite = sprites.WIN_SPRITES_BIG[self.anim_frame % 2]
            self.anim_timer += c.delta_time
            if self.anim_timer > 8 * c.delta_time:
                self.anim_frame += 1
                self.anim_timer = 0

    class Idle_State(State):
        def on_enter(self, owner_object, prev_state):
            if owner_object.animation.mario_size == 'Small_Mario':
                owner_object.animation.current_sprite = sprites.SMALL_MARIO_IDLE
            else:
                owner_object.animation.current_sprite = sprites.BIG_MARIO_IDLE
        
        def on_event(self, event):
            if event == 'jump':
                return Mario.Jump_State()
            elif event == 'move':
                return Mario.Move_State()
            elif event == 'decel':
                return Mario.Decel_State()
            elif event == 'brake':
                return Mario.Brake_State()
            elif event == 'crouch':
                return Mario.Crouch_State()
            return self

    class Jump_State(State):
        def on_event(self, event):
            if event == 'no jump':
                return Mario.No_Jump_State()
            return self

        def on_enter(self, owner_object, prev_state):
            if owner_object.current_mario_state == 'Small_Mario':
                sounds.small_jump.play()
            else:
                sounds.big_jump.play()
        
        def update(self, owner_object):
            owner_object.vel.y = c.JUMP_VELOCITY
            if (not owner_object.spacebar or 
                owner_object.pos.y < owner_object.start_height - c.MAX_JUMP_HEIGHT):
                owner_object.action_states.on_event('no jump')
        
    class No_Jump_State(State):
        def on_event(self, event):
            if event == 'idle':
                return Mario.Idle_State()
            elif event == 'decel':
                return Mario.Decel_State()
            elif event == 'brake':
                return Mario.Brake_State()
            elif event == 'move':
                return Mario.Move_State()
            return self

    class Move_State(State):
        def on_event(self, event):
            if event == 'decel':
                return Mario.Decel_State()
            elif event == 'brake':
                return Mario.Brake_State()
            elif event == 'no jump':
                return Mario.No_Jump_State()
            elif event == 'jump':
                return Mario.Jump_State()
            elif event == 'crouch':
                return Mario.Crouch_State()
            elif event == 'idle':
                return Mario.Idle_State()
            return self

        def update(self, owner_object):
            if owner_object.pressed_left:
                c.ACCELERATION = -c.MARIO_ACCELERATION
            elif owner_object.pressed_right:
                c.ACCELERATION = c.MARIO_ACCELERATION
            owner_object.animation.run_anim()

    class Brake_State(State):
        def on_event(self, event):
            if event == 'move':
                return Mario.Move_State()
            elif event == 'decel':
                return Mario.Decel_State()
            elif event == 'no jump':
                return Mario.No_Jump_State()
            elif event == 'jump':
                return Mario.Jump_State()
            elif event == 'crouch':
                return Mario.Crouch_State()
            elif event == 'idle':
                return Mario.Idle_State()
            return self

        def on_enter(self, owner_object, prev_state):
            c.ACCELERATION = 0
            c.FRICTION = c.BRAKE_FRICTION
            if owner_object.animation.mario_size == 'Small_Mario':
                owner_object.animation.current_sprite = sprites.SMALL_MARIO_BRAKE
            else:
                owner_object.animation.current_sprite = sprites.BIG_MARIO_BRAKE

    class Decel_State(State):
        def on_event(self, event):
            if event == 'idle':
                return Mario.Idle_State()
            elif event == 'brake':
                return Mario.Brake_State()
            elif event == 'move':
                return Mario.Move_State()
            elif event == 'no jump':
                return Mario.No_Jump_State()
            elif event == 'jump':
                return Mario.Jump_State()
            elif event == 'crouch':
                return Mario.Crouch_State()
            return self

        def on_enter(self, owner_object, prev_state):
            c.ACCELERATION = 0
            c.FRICTION = c.DECEL_FRICTION

        def update(self, owner_object):
            owner_object.animation.run_anim()

    class Invincible_State(State):
        def __init__(self):
            self.invincible_timer = 0
            self.blink_timer = 0

        def on_event(self, event):
            if event == 'small mario':
                return Mario.Small_Mario()
            return self

        def update(self, owner_object):
            self.invincible_timer += c.delta_time
            if self.invincible_timer > 40 * c.delta_time:
                owner_object.mario_states.on_event('small mario')

            self.blink_timer += c.delta_time
            if self.blink_timer > 7 * c.delta_time:
                owner_object.animation.current_sprite = sprites.EMPTY_SPRITE
                if self.blink_timer > 14 * c.delta_time:
                    self.blink_timer = 0

        def on_exit(self, owner_object):
            owner_object.animation.reset_anim_vars()

    class Small_Mario(State):
        def on_event(self, event):
            if event == 'grow':
                return Mario.Grow_Mario()
            elif event == 'shrink':
                return Mario.Dead_Mario()
            elif event == 'win':
                return Mario.Win_State()
            elif event == 'dead':
                return Mario.Dead_Mario()
            return self
        
    class Grow_Mario(State):
        def on_event(self, event):
            if event == 'big mario':
                return Mario.Big_Mario()
            if event == 'shrink':
                return Mario.Shrink_Mario()
            return self

        def on_enter(self, owner_object, prev_state):
            owner_object.animation.start_height = owner_object.pos.y
            owner_object.animation.reset_anim_vars()
            owner_object.freeze_movement = True

        def update(self, owner_object):
            owner_object.animation.grow_anim()
            owner_object.pos.y = owner_object.animation.new_y
            if owner_object.animation.anim_frame > 7:
                owner_object.mario_states.on_event('big mario')

        def on_exit(self, owner_object):
            owner_object.rect.h = 96
            owner_object.animation.mario_size = 'Big_Mario'
            owner_object.animation.reset_anim_vars()
            owner_object.freeze_movement = False

    class Big_Mario(State):
        def on_event(self, event):
            if event == 'shrink':
                return Mario.Shrink_Mario()
            elif event == 'dead':
                return Mario.Dead_Mario()
            elif event == 'win':
                return Mario.Win_State()
            return self

    class Shrink_Mario(State):
        def on_event(self, event):
            if event == 'invincible':
                return Mario.Invincible_State()
            if event == 'grow mario':
                return Mario.Grow_Mario()
            return self

        def on_enter(self, owner_object, prev_state):
            owner_object.animation.reset_anim_vars()
            owner_object.animation.start_height = owner_object.pos.y
            owner_object.animation.start_sprite_height = owner_object.animation.current_sprite[3]
            owner_object.freeze_movement = True
            sounds.pipe.play()

        def update(self, owner_object):
            owner_object.animation.shrink_anim()
            owner_object.pos.y = owner_object.animation.new_y
            if owner_object.animation.anim_frame > 7:
                owner_object.mario_states.on_event('invincible')

        def on_exit(self, owner_object):
            owner_object.rect.h = 48
            owner_object.animation.mario_size = 'Small_Mario'
            owner_object.animation.reset_anim_vars()
            owner_object.freeze_movement = False

    class Crouch_State(State):
        def on_event(self, event):
            if event == 'brake':
                return Mario.Brake_State()
            elif event == 'jump':
                return Mario.Jump_State()
            elif event == 'decel':
                return Mario.Decel_State()
            elif event == 'move':
                return Mario.Move_State()
            elif event == 'idle':
                return Mario.Idle_State()
            return self

        def on_enter(self, owner_object, prev_state):
            c.FRICTION = c.BRAKE_FRICTION
            c.ACCELERATION = 0
            owner_object.animation.current_sprite = sprites.MARIO_CROUCH
            owner_object.pos.y += 30
            owner_object.rect.h = owner_object.animation.current_sprite[3]

        def update(self, owner_object):
            c.ACCELERATION = 0
            if owner_object.vel.x == 0:
                if owner_object.pressed_left:
                    owner_object.flip_sprites = True
                if owner_object.pressed_right:
                    owner_object.flip_sprites = False

        def on_exit(self, owner_object):
            owner_object.pos.y -= 31
        
    class Dead_Mario(State):
        def __init__(self):
            self.death_timer = 0

        def on_event(self, event):
            return self

        def on_enter(self, owner_object, prev_state):
            owner_object.animation.current_sprite = sprites.DEAD_MARIO
            owner_object.vel.y = c.DEATH_VEL_Y
            owner_object.vel.x = 0
            owner_object.freeze_movement = True
            owner_object.freeze_input = True
            pg.mixer.music.stop()
            pg.mixer.music.set_endevent(c.DEATH_SONG_END)
            pg.mixer.music.load(sounds.death)
            pg.mixer.music.play()

        def update(self, owner_object):
            self.death_timer += c.delta_time
            if self.death_timer > 20 * c.delta_time:
                accelerate(owner_object, 0, c.GRAVITY)
                owner_object.pos += owner_object.vel * c.delta_time

    class Win_State(State):
        def __init__(self):
            self.animation_step = 0
            self.timer = 0

        def on_event(self, event):
            return self

        def on_enter(self, owner_object, prev_state):
            owner_object.animation.reset_anim_vars()
            owner_object.animation.start_height = owner_object.pos.y
            owner_object.animation.new_y = owner_object.pos.y
            owner_object.pos.x = c.flagpole.pos.x - 16
            owner_object.freeze_movement = True
            owner_object.freeze_input = True
            owner_object.vel = Vector2()
            pg.mixer.music.stop()
            sounds.flagpole_sound.play()

        def update(self, owner_object):

            if self.animation_step == 0:
                owner_object.animation.win_anim_on_flag()
                owner_object.pos.y += 4
                if owner_object.pos.y > c.flagpole.pos.y + c.flagpole.rect.h - 100:
                    self.animation_step = 1

            elif self.animation_step == 1:
                owner_object.pos.x = c.flagpole.pos.x + 24
                owner_object.flip_sprites = True
                self.timer += c.delta_time
                if self.timer > 20 * c.delta_time:
                    owner_object.flip_sprites = False
                    owner_object.freeze_movement = False
                    owner_object.pos.x = c.flagpole.pos.x + c.flagpole.rect.w
                    self.animation_step = 2
                    pg.mixer.music.set_endevent(c.WIN_SONG_END)
                    pg.mixer.music.load(sounds.stage_clear)
                    pg.mixer.music.play()

            elif self.animation_step == 2:
                c.ACCELERATION = c.MARIO_ACCELERATION
                owner_object.pressed_right = True
                if owner_object.pos.x > c.LEVEL_END_X:
                    owner_object.freeze_movement = True
                    c.final_count_down = True

            
            
            



        