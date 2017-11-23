import pygame
import math
from obstacle import Obstacle
from car import Car

class World:

    def __init__(self):
        pygame.init()
        self.displayWidth = 800
        self.displayHeight = 800
        self.screen = pygame.display.set_mode((self.displayWidth, self.displayHeight))
        pygame.display.set_caption('CS182 Final Project')   # text at the top of the window
        self.clock = pygame.time.Clock()
        self.isRunning = True
        self.car = Car(self.displayWidth * 0.45, self.displayHeight * 0.8)
        self.obstacles = [
            Obstacle(0, -10, self.displayWidth, 10),                    # top screen border
            Obstacle(self.displayWidth, 0, 10, self.displayHeight),     # right screen border
            Obstacle(0, self.displayHeight, self.displayWidth, 10),     # bottom screen border
            Obstacle(-10, 0, 10, self.displayHeight),                   # left screen border
            Obstacle(0, 0, 150, 150),
            Obstacle(600, 600, 200, 200),
            Obstacle(400, 200, 175, 250),
            Obstacle(100, 600, 250, 100),
            Obstacle(150, 300, 100, 100),
            Obstacle(300, 0, 300, 75)
        ]
        self.dirInput = 0   # 1 if up-arrow key, -1 if down-arrow key, 0 if no input
        self.rotInput = 0   # 1 if left-arrow key, -1 if right-arrow key, 0 if no input

    def run(self):
        ################## DON'T FORGET TO CITE THIS CODE #########################
        while self.isRunning:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.isRunning = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.rotInput = 1
                    elif event.key == pygame.K_RIGHT:
                        self.rotInput = -1
                    elif event.key == pygame.K_UP:
                        self.dirInput = 1
                    elif event.key == pygame.K_DOWN:
                        self.dirInput = -1
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.rotInput = 0
                    elif event.key == pygame.K_RIGHT:
                        self.rotInput = 0
                    elif event.key == pygame.K_UP:
                        self.dirInput = 0
                    elif event.key == pygame.K_DOWN:
                        self.dirInput = 0
            # pygame is weird and leaves old images on the screen, so fill the background white each frame
            self.screen.fill((255, 255, 255))
        ###########################################################################
            # move the car and check for collisions
            self.car.update(self)
            # redraw all the obstacles
            for obstacle in self.obstacles:
                obstacle.update(self)
            # update the screen
            pygame.display.update()
            # try to run at 60 frames per second (or something, not totally sure)
            self.clock.tick(60)
        pygame.quit()
        quit()




