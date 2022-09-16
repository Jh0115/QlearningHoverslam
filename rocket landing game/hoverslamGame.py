#rocket hoverslam lander 2d game
import pygame
from pygame.locals import *
import random
import sys

pygame.init() #This begins the pygame instance
vec = pygame.math.Vector2 #This defines the game as 2D

#window params
H = 700
W = 700
FPS = 60
pygame.display.set_caption("Hoverslam game")

#physics params
g = 2 #gravitational accel
accel = 5 #engine accel
padW = 30 #landing pad width
padH = 5 #landing pad height

#player info
szX = 10
szY = 50

#game setup
framesPerSec = pygame.time.Clock()
displaySurface = pygame.display.set_mode((W,H))

##--------------------------Classes-----------------------------
class rocket(pygame.sprite.Sprite):
    def __init__(self): #initialization function
        super().__init__()
        self.surf = pygame.Surface((szX,szY))
        self.surf.fill((255,255,255))
        self.rect = self.surf.get_rect(center = (W/2,100))

    def move(self): #define rules of movement
        

class pad(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((padW,padH))
        self.surf.fill((255,0,0))
        self.rect = self.surf.get_rect(center = (random.randint(padW/2,W-padW/2),H-padH/2))

##--------------------------Initialize objects-------------------
barge = pad()

player = rocket() #initialize player rocket

##-----------------------Game loop-----------------------------

while True:
    for event in pygame.event.get():
        if event.type == QUIT: #this closes the game when pressing the exit button
            pygame.quit()
            sys.exit()

    displaySurface.fill((100,100,255)) #this draws the background as blue

    displaySurface.blit(player.surf,player.rect) #update player on screen
    displaySurface.blit(barge.surf,barge.rect) #draw barge on screen

    pygame.display.update()
    framesPerSec.tick(FPS)




















