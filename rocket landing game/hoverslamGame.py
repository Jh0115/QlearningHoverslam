#rocket hoverslam lander 2d game
import pygame
from pygame.locals import *
import random
import sys

pygame.init() #This begins the pygame instance
vec = pygame.math.Vector2 #This defines the game as 2D

#window params
H = 1000
W = 700
FPS = 60
pygame.display.set_caption("Hoverslam game")

#physics params
g = 2 #gravitational accel
accel = 5 #engine accel

#player info
szX = 10
szY = 50

#game setup
framesPerSecond = pygame.time.Clock()
displaySurface = pygame.display.set_mode((W,H))






















