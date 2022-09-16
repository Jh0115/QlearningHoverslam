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
accel = -0.2 #engine accel
t_engine = 500 #milliseconds of engine fuel
startTime = 0
engineState = 2 #state 2 means engine off, 1 is on, 0 is used
padW = 30 #landing pad width
padH = 5 #landing pad height
global padX
global padY
padX = random.randint(padW/2,W-padW/2)
padY = H-padH/2
velMaxInert = 1 #maximum lateral velocity
velMaxLive = 3

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
        global engineState
        global startTime
        pressed_keys = pygame.key.get_pressed()

        #determine y acceleration
        if (pressed_keys[K_UP] or engineState==1) and (engineState==2 or engineState==1):
            #if up key is pressed activate the engine for determined time
            self.acc.y = accel
            if engineState==2:
                engineState = 1
                startTime = pygame.time.get_ticks()
        else:
            self.acc.y = g #otherwise the vertical acceleration is due to gravity

        #determine lateral movement
        if pressed_keys[K_LEFT] and engineState!=1:
            self.acc.x = -0.1
        elif pressed_keys[K_RIGHT] and engineState!=1:
            self.acc.x = 0.1
        if pressed_keys[K_LEFT] and engineState==1:
            self.acc.x = -0.5
        elif pressed_keys[K_RIGHT] and engineState==1:
            self.acc.x = 0.5
        
        #limit lateral velocity
        if engineState==2:
            if self.vel.x<-velMaxInert:
                self.vel.x = -velMaxInert
            if self.vel.x>velMaxInert:
                self.vel.x = velMaxInert
        if engineState!=2:
            if self.vel.x<-velMaxLive:
                self.vel.x = -velMaxLive
            if self.vel.x>velMaxLive:
                self.vel.x = velMaxLive

        #detect ground interaction
        if self.pos.y>=H:
            #we have reached the ground cancel all of our velocity and set our position to the ground
            self.vel = (0,0)
            self.acc.x = 0
            self.pos.y = H

        #detect collision with landing pad
        landing = pygame.sprite.spritecollide(player,bargeGroup,False)
        
        if landing:
            if self.pos.y<=(landing[0].rect.top+10):
                self.pos.y = landing[0].rect.top+1
                self.vel.y = 0
                self.vel.x = 0
                self.acc.x = 0
            else:
                if self.pos.x>padX:
                    self.pos.x = padX+padW/2+szX/2
                    self.vel.x = 0
                    self.acc.x = 0
                if self.pos.x<padX:
                    self.pos.x = padX-padW/2-szX/2
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
        self.surf.fill((255,100,100))
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

    print(engineState)
    if (pygame.time.get_ticks()-startTime)>t_engine and engineState==1:
        #change engine state to 0
        engineState = 0
        
    player.move()




















