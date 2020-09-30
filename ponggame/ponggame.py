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
        self.movement = PadMovement.STOP

        '''Construct the pad image'''
        pad_width = 10
        pad_height = 75
        self.image = Surface((pad_width, pad_height))
        color_white = (255, 255, 255)
        self.image.fill(color_white)
        self.rect = self.image.get_bounding_rect()

        '''Position pad on screen'''
        pad_offset_width = 30
        screen = display.get_surface()
        pad_offset_top = (screen.get_height() - pad_height) / 2
        self.rect.top = pad_offset_top
        if align_right:
            self.rect.right = screen.get_width() - pad_offset_width
        else:
            self.rect.left = pad_offset_width

    def update(self):
        if self.movement == PadMovement.UP:
            self.rect.move_ip((0, -self.speed))
        elif self.movement == PadMovement.DOWN:
            self.rect.move_ip((0, self.speed))

    def move(self, movement):
        self.movement = movement


class Ball(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.speed = 5
        self.dir = (1, 0)

        '''Construct ball image'''
        width = 10
        height = 10
        self.image = Surface((width, height))
        color_white = (255, 255, 255)
        self.image.fill(color_white)
        self.rect = self.image.get_bounding_rect()

        '''Position ball on screen'''
        screen = display.get_surface()
        width_middle = (screen.get_width() - width) / 2
        height_middle = (screen.get_height() - height) / 2
        self.rect.left = width_middle
        self.rect.top = height_middle

    def update(self):
        self.rect.left += self.speed * self.dir[0]
        self.rect.top += self.speed * self.dir[1]


player_left_controls = constants.K_w, constants.K_s
player_right_controls = constants.K_UP, constants.K_DOWN


def main():
    pygame.init()

    '''Initialize screen and background'''
    screen = display.set_mode((800, 400))
    display.set_caption("Pong")
    background = Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    display.flip()
    # pygame.mouse.set_visible(False)

    '''Create game objects'''
    pad_left = Pad(False)
    pad_right = Pad(True)
    ball = Ball()
    allsprites = sprite.Group((pad_left, pad_right, ball))
    clock: Clock = time.Clock()

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

        allsprites.update()

        '''Draw everything'''
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        display.flip()


if __name__ == '__main__':
    main()
