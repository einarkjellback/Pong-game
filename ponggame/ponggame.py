import enum

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
        self.min_speed = 5.0
        self.max_speed = 10.0
        self.speed = self.min_speed
        self.vec: Vector2 = Vector2()
        self.start_x = 1.0
        self.vec.x = self.start_x
        self.vec.y = 0.0
        self.pad_left = pad_left
        self.pad_right = pad_right
        self.acc_xy_error = 0.0, 0.0  # Used to correct accumulated rounding errors in x and y when moving each frame

        '''Construct ball image'''
        width = 10
        height = 10
        self.image = Surface((width, height))
        color_white = (255, 255, 255)
        self.image.fill(color_white)
        self.rect: Rect = self.image.get_bounding_rect()

        '''Position ball on screen'''
        screen = display.get_surface()
        width_middle = (screen.get_width() - width) / 2
        height_middle = (screen.get_height() - height) / 2
        self.START_POS = int(round(width_middle)), int(round(height_middle))
        self.rect.centerx, self.rect.centery = self.START_POS

    def update(self):
        old_vec = Vector2()
        old_vec.x = self.vec.x
        old_vec.y = self.vec.y
        if self.outside_display():
            self.rect.centerx, self.rect.centery = self.START_POS
            self.speed = self.min_speed
            self.start_x *= -1
            self.vec.x = self.start_x
            self.vec.y = 0.0
        else:
            self.handle_pad_collision()
            self.handle_display_collision()
        self.move_ball()
        # if self.speed > self.max_speed:
        #     print(self.speed)

    def move_ball(self):
        """Move ball"""
        delta_x = self.speed * (self.vec.x ** 2) * sgn(self.vec.x)
        delta_y = self.speed * (self.vec.y ** 2) * sgn(self.vec.y)
        error_x = self.acc_xy_error[0]
        error_y = self.acc_xy_error[1]
        delta_x_corrected = round(delta_x + error_x)
        delta_y_corrected = round(delta_y + error_y)
        new_error_x = delta_x - delta_x_corrected
        new_error_y = delta_y - delta_y_corrected
        self.acc_xy_error = error_x + new_error_x, error_y + new_error_y
        self.rect.move_ip(delta_x_corrected, delta_y_corrected)

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
        rect = self.rect
        pad_l = self.pad_left
        pad_r = self.pad_right
        x_axis_normal = Vector2()
        x_axis_normal.x = 0
        x_axis_normal.y = 1

        max_angle = 60
        if rect.right > pad_r.left:
            if rect.bottom > pad_r.top and rect.top < pad_r.bottom:
                rel_diff_pad_center = 2 * ((pad_r.centery - rect.centery) / (pad_r.h + rect.h))
                angle = max_angle * rel_diff_pad_center + 180
                self.vec.from_polar((1, angle))
                self.speed = self.min_speed + self.max_speed * abs(rel_diff_pad_center)
            elif rect.bottom == pad_r.top or rect.top == pad_r.bottom:
                self.vec = self.vec.reflect(x_axis_normal)
        elif rect.left < pad_l.right:
            if rect.bottom > pad_l.top and rect.top < pad_l.bottom:
                rel_diff_pad_center = 2 * ((rect.centery - pad_l.centery) / (pad_l.h + rect.h))
                angle = max_angle * rel_diff_pad_center
                self.vec.from_polar((1, angle))
                self.speed = self.min_speed + self.max_speed * abs(rel_diff_pad_center)
            elif rect.bottom == pad_l.top or rect.top == pad_l.bottom:
                self.vec = self.vec.reflect(x_axis_normal)

    def outside_display(self):
        rect = self.rect
        return rect.left > self.pad_right.right or rect.right < self.pad_left.left


player_left_controls = constants.K_w, constants.K_s
player_right_controls = constants.K_UP, constants.K_DOWN


def main():
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

        '''Control left pad movement'''
        if is_pressed[player_left_controls[0]]:
            pad_left.move(PadMovement.UP)
        elif is_pressed[player_left_controls[1]]:
            pad_left.move(PadMovement.DOWN)
        else:
            pad_left.move(PadMovement.STOP)

        '''Control right pad movement'''
        if is_pressed[player_right_controls[0]]:
            pad_right.move(PadMovement.UP)
        elif is_pressed[player_right_controls[1]]:
            pad_right.move(PadMovement.DOWN)
        else:
            pad_right.move(PadMovement.STOP)
        event.pump()

        all_sprites.update()

        '''Draw everything'''
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)
        display.flip()


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
