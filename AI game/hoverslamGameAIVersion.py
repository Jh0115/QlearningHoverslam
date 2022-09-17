#rocket hoverslam lander 2d game
import pygame
from pygame.locals import *
import random
import sys
import math
import numpy as np

#AI will have m inputs:
#   1. move left
#   2. move right
#   3. activate engine
#   4. do nothing

#AI will have n states
#   1. height above ground
#   2. x displacement from pad
#   3. current engine state
#   4. x speed
#   5. y speed

#nueral network design: 5 input neurons, 4 output neurons, and adaptive hidden layers
math.exp(-0.4*-1770)
def sigmoid(x):
    s = 0.4
    length = len(x)
    x_sigged = x
    for ii in range(0,length):
        if x[ii]<-1000:
            x[ii] = -1000
        x_sigged[ii] = 1/(1+math.exp(-s*x[ii]))
    return x_sigged

def neuronActivation(vals,w,b):
    #vals is a 1 by n vector of neuron activations
    #w is an n by n matrix of axon weights
    #b is a 1 by n vector of biases
    s = np.matmul(w,vals)+b
    act = sigmoid(s) #calculate the activations by using sigmoid function
    return act
    

#-------------------------------Start game program------------------------------
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
t_engine = 1000 #milliseconds of engine fuel
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
landingSpeed = 0
landingDist = 0
landingPad = False

inputNeurons = np.array([[0],[0],[0],[0],[0]]) #these are the neurons that correspond to the above comment
w = [] #this is the weights matrix with axon weights
n = 5
m = 4
for ii in range(0,m): #m number of rows (outputs)
    row = []
    for jj in range(0,n): #n number of columns (axons and inputs)
        row.append(0)
    w.append(row)

# TEMPORARY
w = [[0,5,0,0,0],[0,-5,0,0,0],[0.2,0,0,0,0.5],[0,0,0,0,-0.1]]
print(w)
# TEMPORARY
b = np.array([[0],[0],[-10],[50]]) #this is the bias vector for each new neuron

outputNeurons = neuronActivation(inputNeurons,w,b)

#game setup
framesPerSec = pygame.time.Clock()
displaySurface = pygame.display.set_mode((W,H))
gameOverFlag = False

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
        global gameOverFlag
        global landingSpeed
        global landingDist
        global landingPad
        global inputNeurons
        global ouputNeurons
        pressed_keys = pygame.key.get_pressed()
        landingSpeed = math.sqrt(self.vel.x**2+self.vel.y**2)
        landingDist = abs(padX-self.pos.x)
        if self.pos.x<(padX+0.5*padW) and self.pos.x>(padX-0.5*padW):
            landingPad = 10 #points for keeping score
        else:
            landingPad = -20 #points for keeping score

        #update the inputs to the neural network
        inputNeurons = np.array([[self.pos.y],[(self.pos.x-padX)],[engineState],[self.vel.x],[self.vel.y]])

        #through neural network calculate key presses
        outputNeurons = neuronActivation(inputNeurons,w,b)
        #print(outputNeurons)

        #given neural network output simulate key presses
        #adding these extra variables means i can still take control of the game without changing much code
        upkey = False
        leftkey = False
        rightkey = False

        if outputNeurons[0]==max(outputNeurons):
            leftkey = True
        elif outputNeurons[1]==max(outputNeurons):
            rightkey = True
        elif outputNeurons[2]==max(outputNeurons):
            upkey = True
        
            

        #determine y acceleration
        if ((pressed_keys[K_UP] or upkey) or engineState==1) and (engineState==2 or engineState==1):
            #if up key is pressed activate the engine for determined time
            self.acc.y = accel
            if engineState==2:
                engineState = 1
                startTime = pygame.time.get_ticks()
        else:
            self.acc.y = g #otherwise the vertical acceleration is due to gravity

        #determine lateral movement
        if (pressed_keys[K_LEFT] or leftkey) and engineState!=1:
            self.acc.x = -0.1
        elif (pressed_keys[K_RIGHT] or rightkey) and engineState!=1:
            self.acc.x = 0.1
        if (pressed_keys[K_LEFT] or leftkey) and engineState==1:
            self.acc.x = -0.5
        elif (pressed_keys[K_RIGHT] or rightkey) and engineState==1:
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
            self.vel = vec(0,0)
            self.acc.x = 0
            self.pos.y = H
            gameOverFlag = True

        #detect collision with landing pad
        landing = pygame.sprite.spritecollide(player,bargeGroup,False)
        if landing:
            if self.pos.y<=(landing[0].rect.top+10):
                self.pos.y = landing[0].rect.top+1
                self.vel = vec(0,0)
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
            gameOverFlag = True
                
        
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

while True:

    ##--------------------------Initialize objects-------------------
    #physics params
    startTime = 0
    engineState = 2 #state 2 means engine off, 1 is on, 0 is used
    padX = random.randint(padW/2,W-padW/2)
    gameOverFlag = False

    barge = pad() #initialize landing zone
    bargeGroup = pygame.sprite.Group()
    bargeGroup.add(barge)

    player = rocket() #initialize player rocket

    ##-----------------------Game loop-----------------------------

    restart = False
    while not restart:
        for event in pygame.event.get():
            if event.type == QUIT: #this closes the game when pressing the exit button
                pygame.quit()
                sys.exit()

        displaySurface.fill((100,100,255)) #this draws the background as blue

        displaySurface.blit(player.surf,player.rect) #update player on screen
        displaySurface.blit(barge.surf,barge.rect) #draw barge on screen

        pygame.display.update()
        framesPerSec.tick(FPS)

        if (pygame.time.get_ticks()-startTime)>t_engine and engineState==1:
            #change engine state to 0
            engineState = 0
            
        player.move()

        keys = pygame.key.get_pressed()
        if keys[K_r]:
            restart = True
        if gameOverFlag:
            #report final results and call for a restart
            score = (landingPad)+(10/landingSpeed)+(10/landingDist)
            if score<0:
                score = 0
            print(score)
            restart = True




















