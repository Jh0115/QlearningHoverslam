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
g = 0.2 #gravitational accel
accel = -0.5 #engine accel
t_engine = 2 #seconds of engine fuel
global engine_state
engine_state = 2 #state 2 means engine off, 1 is on, 0 is used
padW = 30 #landing pad width
padH = 50 #landing pad height
global padX
global padY
padX = random.randint(padW/2,W-padW/2)
padY = H-padH/2
velMax = 1 #maximum lateral velocity

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
        self.rect = self.surf.get_rect()

        self.pos = vec((W/2,100))
        self.vel = vec(0,0)
        self.acc = vec(0,g)

    def move(self): #define rules of movement
        self.acc = vec(0,0)

        pressed_keys = pygame.key.get_pressed()

        #determine y acceleration
        if pressed_keys[K_UP] and (engine_state==2 or engine_state==1):
            #if up key is pressed activate the engine for determined time
            self.acc.y = accel
        else:
            self.acc.y = g #otherwise the vertical acceleration is due to gravity

        #determine lateral movement
        if pressed_keys[K_LEFT]:
            self.acc.x = -0.1
        elif pressed_keys[K_RIGHT]:
            self.acc.x = 0.1
        
        #limit lateral velocity
        if self.vel.x<-velMax:
            self.vel.x = -velMax
        if self.vel.x>velMax:
            self.vel.x = velMax

        #detect ground interaction
        if self.pos.y>=H:
            #we have reached the ground cancel all of our velocity and set our position to the ground
            self.vel = (0,0)
            self.acc.x = 0
            self.pos.y = H

        #detect collision with landing pad
        landing = pygame.sprite.spritecollide(player,bargeGroup,False)
        
        if landing:
            self.pos.y = landing[0].rect.top+1
            self.vel.y = 0
            self.vel.x = 0
            self.acc.x = 0
                
        
        #update state variables
        self.vel+=self.acc
        self.pos+=self.vel+0.5*self.acc

        self.rect.midbottom = self.pos
            

class pad(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((padW,padH))
        self.surf.fill((255,0,0))
        self.rect = self.surf.get_rect(center = ((padX,padY)))

##--------------------------Initialize objects-------------------
barge = pad() #initialize landing zone
bargeGroup = pygame.sprite.Group()
bargeGroup.add(barge)

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

    player.move()




















