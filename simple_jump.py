#!/usr/bin/env python

"""
    Author: muchuanyun


"""

import pygame
import os

from pygame.locals import *
from pygame.compat import geterror

if not pygame.font:
    print('Warning, fonts disabled')
if not pygame.mixer:
    print('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

window_width = 800
window_height = 672

ground_y = window_height * 0.9
velocity = 10
player_speed = 10

playerPosX = 10

black = (0,0,0)
white = (255, 255, 255)
darkgreen = (34,139,34)
darkbrown = (139,69,19)
darkgrey = (105,105,105)


# Resource handling functions
def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()


def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound


# Game object classes

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('idle.png', -1)
        self.rect.bottomleft = (playerPosX, ground_y)

        self.stand_image = self.image
        self.jump_image, _ = load_image('jump.png', -1)
        self.speed = player_speed
        self.m = 2
        self.v = velocity
        self.isjump = False
        self.iswalk = False

    def stand(self):
        self.iswalk = False

    def walk(self):
        """
        walk horizontally
        """
        self.iswalk = True

    def jump(self):
        self.isjump = True

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        if self.alive():
            if self.iswalk:
                self.rect.move_ip((self.speed, 0))

            if self.isjump:
                if self.v > 0:
                    F = ( 0.5 * self.m * (self.v*self.v) )
                else:
                    F = -( 0.5 * self.m * (self.v*self.v) )

                self.rect.move_ip((self.speed*0.5, -F))
                self.image = self.jump_image

                self.v = self.v - 1

                if self.rect.bottom >= ground_y:
                    self.rect.bottom = ground_y
                    self.isjump = False
                    self.image = self.stand_image
                    self.v = velocity


def main():

    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption('Mario Jump')

    # create background
    background = pygame.Surface((window_width, ground_y))
    background = background.convert()
    background.fill(darkgreen)
    screen.blit(background, (0, 0))
    ground = pygame.Surface((window_width, window_height - ground_y))
    ground = ground.convert()
    ground.fill(darkgrey)
    screen.blit(background, (0, ground_y))

    pygame.display.flip()

    clock = pygame.time.Clock()
    player = Player()

    allsprites = pygame.sprite.RenderPlain((player))

    running = True
    while running:
        clock.tick(40)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
            elif event.type == KEYDOWN and event.key == K_SPACE:
                player.jump()
            elif event.type == KEYDOWN and event.key == K_RIGHT:
                player.walk()
            elif event.type == KEYUP and event.key == K_RIGHT:
                player.stand()

        allsprites.update()

        #Draw Everything
        screen.blit(background, (0, 0))
        screen.blit(ground, (0, ground_y))
        allsprites.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
