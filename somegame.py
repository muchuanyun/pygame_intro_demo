#!/usr/bin/env python

"""
    Author: muchuanyun

    A demo of Mario Jump.

"""

import pygame
import os

from pygame.locals import *
from pygame.compat import geterror

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')


# Resource handling functions
def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    #image = image.convert_alpha()
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


# Constants and initialization
black = (0,0,0)
white = (255, 255, 255)
darkgreen = (34,139,34)
darkbrown = (139,69,19)
darkgrey = (105,105,105)

window_width = 800
window_height = 672

ground_y = window_height * 0.9
velocity = 10
player_speed = 10
player_box_posX = 0


# Game object classes
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_l, self.rect = load_image('enemy_small1.png', -1)
        self.image_r, _  = load_image('enemy_small2.png', -1)
        self.image = self.image_l
        self.rect.bottomleft = (window_width, ground_y)
        self.status = 1
        self.speed = -4

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        if self.alive:
            self.rect.move_ip((self.speed, 0))
            self.status += 1
            if self.status <= 10:
                self.image = self.image_l
            elif self.status <= 20:
                self.image = self.image_r
            else:
                self.status = 1

            if self.rect.right < 0:
                self.rect.left = window_width


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('idle.png', -1)
        self.rect.bottomleft = (player_box_posX, ground_y)

        self.stand_image = self.image
        self.jump_image, _ = load_image('jump.png', -1)
        self.speed = player_speed
        self.cur_speed = 0
        self.m = 2
        self.v = velocity
        self.isjump = False
        self.iswalk = False

    def walk(self):
        """
        walk horizontally
        """
        self.iswalk = True

    def jump(self):
        self.isjump = True

    def stand(self):
        self.iswalk = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        global player_box_posX
        if self.alive():
            self.rect.left = player_box_posX

            if self.iswalk:
                self.rect.move_ip((self.speed, 0))
                self.cur_speed = self.speed
            else:
                self.cur_speed = 0

            if self.isjump:
                if self.v > 0:
                    F = (0.5 * self.m * (self.v*self.v))
                else:
                    F = -(0.5 * self.m * (self.v*self.v))

                self.rect.move_ip((self.speed, -F))
                self.image = self.jump_image
                self.cur_speed = self.speed

                self.v = self.v - 1

                if self.rect.bottom >= ground_y:
                    self.rect.bottom = ground_y
                    self.isjump = False
                    self.iswalk = False
                    self.image = self.stand_image
                    self.v = velocity

            player_box_posX = self.rect.left


def main():

    pygame.init()
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption('Mario Jump')

    # create background
    bg, bg_rect = load_image('level_large.jpg')
    bg_width, bg_height = bg_rect.size
    screen.blit(bg, (0, 0))

    if pygame.font:
        font = pygame.font.Font(None, 36)
        text = font.render("MARIO GO", 1, darkgrey)
        textpos = text.get_rect(centerx=window_width/2)
        screen.blit(text, textpos)

    # display background
    pygame.display.flip()

    # prepare game objects
    clock = pygame.time.Clock()
    bgm = load_sound('SuperMarioBros.ogg')
    player = Player()
    goomba = Enemy()
    allsprites = pygame.sprite.RenderPlain((player, goomba))

    global player_box_posX
    # For scrolling
    stage_width = bg_width
    stage_posX = 0
    half_window_width = window_width / 2
    start_scrolling_pos = half_window_width
    player_posX = player_box_posX
    player_box_width = player.rect.width

    running = True
    while running:
        clock.tick(40)
        bgm.play(-1)

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

        # if player.rect.colliderect(goomba.rect):
        #    player.kill()
        #    bgm.stop()

        # For scrolling
        player_posX += player.cur_speed
        if player_posX > stage_width - player_box_width:
            player_posX = stage_width - player_box_width
        if player_posX < 0:
            player_posX = 0
        if player_posX < start_scrolling_pos:
            player_box_posX = player_posX
        elif player_posX > stage_width - start_scrolling_pos:
            player_box_posX = player_posX - stage_width + window_width
        else:
            player_box_posX = start_scrolling_pos
            stage_posX -= player.cur_speed

        rel_x = stage_posX % bg_width
        screen.blit(bg, (rel_x - bg_width, 0))
        if rel_x < window_width:
            screen.blit(bg, (rel_x, 0))

        #Draw Everything
        allsprites.draw(screen)
        screen.blit(text, textpos)
        pygame.display.flip()

    bgm.stop()
    pygame.quit()

if __name__ == '__main__':
    main()
