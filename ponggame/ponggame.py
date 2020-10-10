import enum
from math import ceil

import pygame
from pygame import *
from pygame import constants
from pygame.time import Clock


class PadMovement(enum.Enum):
    UP = 1
    DOWN = 2
    STOP = 3


class Pad(sprite.Sprite):
    def __init__(self, align_right):
        sprite.Sprite.__init__(self)
        self.speed = 5
        self.dir = PadMovement.STOP

        '''Construct the pad image'''
        pad_width = 10
        pad_height = 75
        self.image = Surface((pad_width, pad_height))
        color_white = (255, 255, 255)
        self.image.fill(color_white)
        self.rect = self.image.get_bounding_rect()

        '''Position pad on screen'''
        self.offset_width = 30
        screen = display.get_surface()
        screen_middle = screen.get_height() / 2
        self.rect.centery = int(round(screen_middle))
        if align_right:
            self.rect.right = screen.get_width() - self.offset_width
        else:
            self.rect.left = self.offset_width

    def update(self):
        dir_ = self.dir
        screen: Rect = display.get_surface().get_rect()
        rect = self.rect
        if dir_ == PadMovement.UP and screen.top < rect.top:
            rect.move_ip((0, -self.speed))
        elif dir_ == PadMovement.DOWN and screen.bottom > rect.bottom:
            rect.move_ip((0, self.speed))

    def move(self, movement):
        self.dir = movement


def sgn(val):
    if val < 0:
        return -1
    elif val > 0:
        return 1
    return 0


class Ball(sprite.Sprite):
    def __init__(self, pad_left, pad_right):
        sprite.Sprite.__init__(self)
        self.pad_left = pad_left
        self.pad_right = pad_right

        self.MAX_ANGLE = 60
        self.MIN_SPEED = 5.0
        self.MAX_SPEED = 10.0
        self.SUPER_SPEED = self.MAX_SPEED * 1.2  # Ball's speed if it collides with pad ends
        self.speed = self.MIN_SPEED
        self.START_X = 1.0
        self.START_Y = 0.0
        self.vec: Vector2 = Vector2()
        self.xy_error = 0.0, 0.0  # Used to correct rounding errors in x and y when moving each frame

        self.make_image()

        """Position ball on screen"""
        screen = display.get_surface().get_rect()
        width_middle = (screen.w - self.rect.w) / 2
        height_middle = (screen.h - self.rect.h) / 2
        self.START_POS = int(round(width_middle)), int(round(height_middle))
        self.reset_ball()

    def make_image(self):
        """Construct ball image"""
        width = 10
        height = 10
        self.image = Surface((width, height))
        color_white = (255, 255, 255)
        self.image.fill(color_white)
        self.rect: Rect = self.image.get_bounding_rect()

    def update(self):
        if not self.handle_outside_display():
            self.handle_pad_collision()
            self.handle_display_collision()
        self.move_ball()

    def move_ball(self):
        """Move ball and corrects rounding errors in trajectory from last update"""
        delta_x = self.speed * (self.vec.x ** 2) * sgn(self.vec.x)
        delta_y = self.speed * (self.vec.y ** 2) * sgn(self.vec.y)

        error_x = self.xy_error[0]
        error_y = self.xy_error[1]

        delta_x_corrected = delta_x + error_x
        delta_y_corrected = delta_y + error_y

        delta_x_corr_rounded = round(delta_x_corrected)
        delta_y_corr_rounded = round(delta_y_corrected)

        new_error_x = delta_x_corrected - delta_x_corr_rounded
        new_error_y = delta_y_corrected - delta_y_corr_rounded

        self.xy_error = new_error_x, new_error_y
        self.rect.move_ip(delta_x_corr_rounded, delta_y_corr_rounded)

    def handle_display_collision(self):
        """Check and handle collision with top and bottom of display"""
        screen = display.get_surface().get_rect()
        y_axis = Vector2()
        y_axis.x = 0
        y_axis.y = 1
        if self.rect.top < screen.top or self.rect.bottom > screen.bottom:
            self.vec = self.vec.reflect(y_axis)

    def handle_pad_collision(self):
        """Check and handle collision with pads"""
        if not self.handle_long_side_collision():
            self.handle_end_collision()

    def handle_end_collision(self):
        """Check and handle collision with either ends of pads. Returns True if collision with either ends"""
        collided = self.check_end_collision(False) or self.check_end_collision(True)
        if collided:
            x_axis_normal = Vector2()
            x_axis_normal.x = 0
            x_axis_normal.y = 1
            self.vec.x *= -1
            self.vec.y *= -1
            self.speed = self.SUPER_SPEED
        return collided

    def check_end_collision(self, left_pad):
        """Checks if the ball is colliding with either the top or bottom of the pads"""
        delta_y = max(1, ceil((self.speed * self.vec.y ** 2) / 2.0))
        rect: Rect = self.rect
        pad = self.pad_left if left_pad else self.pad_right
        collision_zone_x = 0.5 * (pad.w + rect.w)
        is_aligned_x = abs(pad.centerx - rect.centerx) < collision_zone_x
        is_aligned_top = pad.top - delta_y <= rect.bottom <= pad.top + delta_y
        is_aligned_bottom = pad.bottom - delta_y <= rect.top <= pad.bottom + delta_y
        is_going_down = self.vec.y > 0
        is_going_up = self.vec.y < 0
        return is_aligned_x and ((is_aligned_top and is_going_down) or (is_aligned_bottom and is_going_up))

    def handle_long_side_collision(self):
        """Check and handle collision with pad broad sides. Returns True if collision with either pads' broad sides"""
        check_left = False
        collided_right = self.check_long_side_collision(check_left)
        if collided_right:
            self.reflect_from_long_side(check_left)
            return collided_right
        collided_left = self.check_long_side_collision(True)
        if collided_left:
            self.reflect_from_long_side(True)
        return collided_left

    def reflect_from_long_side(self, left_pad):
        """Reflects ball from a pad's long side"""
        rect = self.rect
        pad = self.pad_left if left_pad else self.pad_right
        rel_diff_pad_center = 2 * ((rect.centery - pad.centery) / (pad.h + rect.h))
        angle = self.MAX_ANGLE * rel_diff_pad_center
        angle *= 1 if left_pad else -1
        angle += 0 if left_pad else 180
        self.vec.from_polar((1, angle))
        self.speed = (self.MAX_SPEED - self.MIN_SPEED) * abs(rel_diff_pad_center) + self.MIN_SPEED

    def check_long_side_collision(self, left_pad):
        """Checks if ball is colliding with long sides of pads"""
        pad = self.pad_left if left_pad else self.pad_right
        rect = self.rect
        pad_side = pad.right if left_pad else pad.left
        ball_side = rect.left if left_pad else rect.right

        delta_x = ceil((self.speed * self.vec.x ** 2) / 2)
        is_aligned_x = pad_side - delta_x <= ball_side <= pad_side + delta_x
        is_aligned_y = rect.bottom > pad.top and rect.top < pad.bottom
        return is_aligned_x and is_aligned_y

    def handle_outside_display(self):
        """Checks if the ball is outside the display and resets the Ball to start position if outside"""
        rect = self.rect
        screen = display.get_surface().get_rect()
        updates_after_disappearing_before_reset = 60
        delta = self.speed * updates_after_disappearing_before_reset
        outside_display = rect.left > screen.right + delta or rect.right < screen.left - delta
        if outside_display:
            self.reset_ball()
        return outside_display

    def reset_ball(self):
        """Resets the ball to the start position"""
        self.rect.centerx, self.rect.centery = self.START_POS
        self.speed = self.MIN_SPEED
        self.START_X *= -1
        self.vec.x = self.START_X
        self.vec.y = self.START_Y


def main():
    LEFT_CONTROLS = constants.K_w, constants.K_s
    RIGHT_CONTROLS = constants.K_UP, constants.K_DOWN

    pygame.init()
    background, screen = init_screen()
    all_sprites, pad_left, pad_right = create_game_objects()
    clock = Clock()

    '''Main loop'''
    run_game = True
    while run_game:
        '''Set FPS'''
        clock.tick_busy_loop(60)

        '''Handle input events'''
        is_pressed = key.get_pressed()
        if is_pressed[constants.K_ESCAPE]:
            run_game = False
        handle_pad_movement(LEFT_CONTROLS, pad_left)
        handle_pad_movement(RIGHT_CONTROLS, pad_right)
        event.pump()

        all_sprites.update()

        '''Draw everything'''
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        display.flip()


def handle_pad_movement(controls, pad):
    """Control pad movement"""
    is_pressed = key.get_pressed()
    if is_pressed[controls[0]]:
        pad.move(PadMovement.UP)
    elif is_pressed[controls[1]]:
        pad.move(PadMovement.DOWN)
    else:
        pad.move(PadMovement.STOP)


def init_screen():
    """Initialize screen and background"""
    screen = display.set_mode((500, 400))
    display.set_caption("Pong")
    background = Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    display.flip()
    pygame.mouse.set_visible(False)
    return background, screen


def create_game_objects():
    """Create game objects"""
    pad_left = Pad(False)
    pad_right = Pad(True)
    ball = Ball(pad_left.rect, pad_right.rect)
    allsprites = sprite.Group(pad_left, pad_right, ball)
    return allsprites, pad_left, pad_right


if __name__ == '__main__':
    main()
