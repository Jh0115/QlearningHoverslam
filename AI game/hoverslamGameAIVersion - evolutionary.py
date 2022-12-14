#rocket hoverslam lander 2d game
import pygame
from pygame.locals import *
import random
import sys
import math
import numpy as np
import heapq

#AI will have m inputs:
#   1. move left
#   2. move right
#   3. activate engine
#   4. do nothing

#AI will have n states
#   1. height above ground
#   2. x displacement from pad
#   3. engine availability
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

def neuronActivation(vals,ww,bb):
    #vals is a 1 by n vector of neuron activations
    #w is an n by n matrix of axon weights
    #b is a 1 by n vector of biases
    s = np.matmul(ww,vals)+bb
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
padW = 60 #landing pad width
padH = 10 #landing pad height
global padX
global padY
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
##w = [[0,1,0,0.1,0],
##     [0,-1,0,0.1,0],
##     [0.1,-0.2,1,-0.1,1],
##     [-0.1,0,0,0,-0.2]]
# TEMPORARY

##b = np.array([[5],[5],[-10],[90]]) #this is the bias vector for each new neuron
b = np.array([[0],[0],[0],[0]])

outputNeurons = neuronActivation(inputNeurons,w,b)

#game setup
framesPerSec = pygame.time.Clock()
displaySurface = pygame.display.set_mode((W,H))
gameOverFlag = False
batchNum = 100 #how many games to play for each generation

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
            landingPad = 0 #points for keeping score

        #update the inputs to the neural network
        if engineState==2:
            engineInfo = 1
        else:
            engineInfo = -50

        inputNeurons = []
        inputNeurons = np.array([[self.pos.y],[(self.pos.x-padX)],[engineInfo],[self.vel.x],[self.vel.y]])
        
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

        #if engineState<2:
            #print(outputNeurons)
            

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
        elif self.pos.y<0:
            gameOverFlag = True
            landingPad = 0
            landingSpeed = 9999
            landingDist = 9999

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

l = 0
wBatch = []
bBatch = []
sBatch = []
intervalW = []

origInt = 1000 #this is the original interval of random values for all weights and biases
for ii in range(0,m): #m number of rows (outputs)
    row = []
    for jj in range(0,n): #n number of columns (axons and inputs)
        row.append(origInt)
    intervalW.append(row)

intervalB = np.array([[origInt],[origInt],[origInt],[origInt]])

wBestPrev = w
bBestPrev = b
gNum = 1

while True:

    ##--------------------------Initialize objects-------------------
    #physics params
    startTime = 0
    engineState = 2 #state 2 means engine off, 1 is on, 0 is used
    padX = random.randint(W/2-150,W/2+150)
    gameOverFlag = False

    barge = pad() #initialize landing zone
    bargeGroup = pygame.sprite.Group()
    bargeGroup.add(barge)

    player = rocket() #initialize player rocket

    ##-----------------------Game loop-----------------------------

    restart = False
    l += 1
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
            if landingDist<0.1:
                landingDist = 0.1
            if landingSpeed<0.01:
                landingSpeed = 0.01
            score = (landingPad)+(100/landingSpeed)+(10/landingDist)
            if score<0:
                score = 0
            restart = True

    ##------------------------Neural network evolution--------------------------------


    ## if we are not done with this batch, save the score and network params
    if l<batchNum:
        #save the w matrix, b vector, and score
        wBatch.append(w)
        bBatch.append(b)
        sBatch.append(score)

        #randomize the next player with values based on previous generation variance
        w = []
        for ii in range(0,m): #m number of rows (outputs)
            row = []
            for jj in range(0,n): #n number of columns (axons and inputs)
                wLow = wBestPrev[ii][jj]-intervalW[ii][jj]
                wHigh = wBestPrev[ii][jj]+intervalW[ii][jj]
                randVal = random.uniform(wLow,wHigh)
                row.append(randVal)
            w.append(row)

        randVal1 = random.uniform((bBestPrev[0,0]-intervalB[0,0]),(bBestPrev[0,0]+intervalB[0,0]))
        randVal2 = random.uniform((bBestPrev[1,0]-intervalB[1,0]),(bBestPrev[1,0]+intervalB[1,0]))
        randVal3 = random.uniform((bBestPrev[2,0]-intervalB[2,0]),(bBestPrev[2,0]+intervalB[2,0]))
        randVal4 = random.uniform((bBestPrev[3,0]-intervalB[3,0]),(bBestPrev[3,0]+intervalB[3,0]))
        b = []
        b = np.array([[randVal1],[randVal2],[randVal3],[randVal4]])
        
    elif l>=batchNum:    
        ## if this batch is done, evolve based on best performers.
        ## we will shrink the interval of randomness in accordance
        ## with the variance between the top players.

        ## Then we will assume the "best previous player" was a weighted average of the
        ## top players weighted by score

        ## step 1: determine top 10 players
        nn = 10
        sTT = heapq.nlargest(nn,sBatch)
        indexTT = []
        
        for ii in range(0,nn):
            indexTT.append(sBatch.index(sTT[ii]))

        wTT = []
        for ii in range(0,nn):
            wTT.append(wBatch[:][:][indexTT[ii]])

        bTT = []
        for ii in range(0,nn):
            bTT.append(bBatch[:][indexTT[ii]])

        ## step 2: calculate variance values and update randomness intervals
        wAvg = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
        wVar = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
        for ii in range(0,m):
            for jj in range(0,n):
                for kk in range(0,nn):
                    wAvg[ii][jj] += wTT[kk][ii][jj]
                wAvg[ii][jj] = wAvg[ii][jj]/nn
                
        for ii in range(0,m):
            for jj in range(0,n):
                for kk in range(0,nn):
                    wVar[ii][jj] += ((wTT[kk][ii][jj]-wAvg[ii][jj])**2)/(nn-1)
                ## at most we lower the interval by p percent as dictated by the following equation
                intervalW[ii][jj] = intervalW[ii][jj]-((1000000-wVar[ii][jj])/1000000)*origInt

        bAvg = [[0],[0],[0],[0]]
        bVar = [[0],[0],[0],[0]]
        for ii in range(0,m):
            for jj in range(0,nn):
                bAvg[ii][0] += bTT[jj][ii]
            bAvg[ii][0] = bAvg[ii][0]/nn
            
        for ii in range(0,m):
            for jj in range(0,nn):
                bVar[ii][0] += ((bTT[jj][ii]-bAvg[ii][0])**2)/(nn-1)
            intervalB[ii][0] = intervalB[ii][0]-((1000000-bVar[ii][0])/1000000)*origInt

        ## step 3: calculate "best previous player" using weighted average
        for ii in range(0,m):
            for jj in range(0,n):
                wWeighted = 0
                s_sum = 0
                for kk in range(0,nn):
                    wWeighted += (wTT[kk][ii][jj])*sTT[kk]
                    s_sum += sTT[kk]
                wBestPrev[ii][jj] = wWeighted/s_sum
                    
        for ii in range(0,m):
            bWeighted = 0
            s_sum = 0
            for jj in range(0,nn):
                bWeighted += bTT[jj][ii]*sTT[jj]
                s_sum += sTT[jj]
            bBestPrev[ii][0] = bWeighted/s_sum

        ## step 4: reset for next batch
        l = 0
        wBatch = []
        bBatch = []
        sBatch = []
        gNum += 1
        print(str(gNum)+"   "+str(sTT[0])+"   "+str(bBestPrev[0][0]))
        




















