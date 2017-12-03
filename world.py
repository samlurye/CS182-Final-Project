import pygame
import math
import random
from obstacle import Obstacle
from car import *
import time
from PRM import *
from customer import *


class World:

    def __init__(self):
        pygame.init()
        self.displayWidth = 800
        self.displayHeight = 800
        self.screen = pygame.display.set_mode((self.displayWidth, self.displayHeight))
        pygame.display.set_caption('CS182 Final Project')   # text at the top of the window
        self.clock = pygame.time.Clock()
        self.isRunning = True
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
        #self.cars = [DataCollectionAgent(0.45 * self.displayWidth, 0.8 * self.displayWidth, self)]
        self.numCars = 1
        self.cars = [CustomerAgent(0.45 * self.displayWidth, 0.8 * self.displayWidth, self, i) for i in range(self.numCars)]

        # the self refers to the world
        self.customers = Customers(self)
        self.kdtreeStart = (0.45 * self.displayWidth, 0.8 * self.displayWidth)
        self.prm = PRM(self)
        for car in self.cars:
            car.prm = self.prm
        self.dirInput = 0   # 1 if up-arrow key, -1 if down-arrow key, 0 if no input
        self.rotInput = 0   # 1 if left-arrow key, -1 if right-arrow key, 0 if no input
        self.frames = 0

    def run(self):
        ################## DON'T FORGET TO CITE THIS CODE #########################
        while self.isRunning:
            self.frames += 1
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
                    # press 'p' for new passenger
                    if event.key == pygame.K_p:
                        self.customers.newCustomer(self)
                        self.customers.newCustomer(self)
                        self.customers.newCustomer(self)
                        self.customers.newCustomer(self)
                        self.customers.newCustomer(self)
                        for customer in self.customers.waitingCustomers:
                            print customer
                    # clear all waiting customers
                    if event.key == pygame.K_c:
                        self.customers.waitingCustomers = []

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
            for car in self.cars:
                if car.i >= len(car.currentPath) - 1:
                    ######## QUEUE PICKUP AGENT (Does Customer 1 then 2...) ########
                    # if len(self.customers.waitingCustomers) != 0:
                    #     nextCustomer = self.customers.waitingCustomers.pop(0)
                    #     car.setPath(car.xy, nextCustomer["startCoords"], nextCustomer["endCoords"], self)
                    #     self.customers.drivingCustomers.append(nextCustomer)
                        # self.customers.finishedRide(self, nextCustomer["numCustomer"])

                    ######## RANDOM PICKUP AGENT (Picks up customers randomly) ########
                    if len(self.customers.waitingCustomers) != 0:
                        nextCustomer = self.customers.waitingCustomers.pop(random.randint(0,len(self.customers.waitingCustomers)) - 1)
                        car.setPath(car.xy, nextCustomer["startCoords"], nextCustomer["endCoords"], self)
                        self.customers.drivingCustomers.append(nextCustomer)
                    
                        
                        

                    # old code that would send the cars to random spots
                    # if car.endPoints:
                    #     car.setPath(car.endPoints[1], car.prm.sample(self), self)
                    # else:
                    #     car.setPath(car.prm.sample(self), car.prm.sample(self), self)
                car.update(self)
            # redraw all the obstacles
            for obstacle in self.obstacles:
                obstacle.update(self)
            self.customers.update(self)
            # update the screen
            pygame.display.update()
            # try to run at 60 frames per second (or something, not totally sure)
            self.clock.tick(20)
        pygame.quit()
        quit()




