import enum
from math import sin, cos, pi

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
        self.offset_top = (screen.get_height() - pad_height) / 2
        self.rect.top = self.offset_top
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


def get_norm_vector(angle):
    rad = pi / 180 * angle
    return cos(rad), sin(rad)


def reflect(dir_):
    return dir_[0], -dir_[1]


class Ball(sprite.Sprite):
    def __init__(self, pad_left, pad_right):
        sprite.Sprite.__init__(self)
        self.speed = 5
        self.dir = (1.0, 0.0)
        self.pad_left = pad_left
        self.pad_right = pad_right

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
        self.rect.left = width_middle
        self.rect.top = height_middle

    def update(self):
        rect = self.rect
        pad_r: Rect = self.pad_right
        pad_l: Rect = self.pad_left
        dir_ = self.dir

        '''Check and handle collision with pads'''
        if rect.right > pad_r.left and rect.bottom > pad_r.top and rect.top < pad_r.bottom:
            angle = 150 + (80 * (pad_r.top - rect.y) / pad_r.height)
            self.dir = get_norm_vector(angle)
            self.rect.x -= 8
        elif rect.left < pad_l.right and rect.bottom > pad_l.top and rect.top < pad_l.bottom:
            angle = 60 * ((pad_l.top - rect.y) / pad_l.height - 0.5)
            self.dir = get_norm_vector(angle)
            self.rect.x += 8

        '''Check collision with top and bottom of display'''
        screen = display.get_surface().get_rect()
        if rect.top < screen.top:
            self.dir = reflect(dir_)
            self.rect.y += 8    # To avoid ball getting stuck in display
        elif rect.bottom > screen.bottom:
            self.dir = reflect(dir_)
            self.rect.y -= 8    # To avoid ball getting stuck in display

        '''Move ball'''
        rect.left += self.speed * dir_[0]
        rect.top += self.speed * dir_[1]


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
        clock.tick(60)

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
    screen = display.set_mode((800, 400))
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
