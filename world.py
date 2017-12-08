import sys
import pygame
import math
import random
from obstacle import Obstacle
from car import *
import time
from PRM import *
from customer import *
from clusteringMultiagent import *
from efficiencyTracker import * 

class World:

    options = {"PASSENGER_PICKUP" : 0,
           "RANDOM_NAV" : 1,
           "MAP_ONLY" : 2,
           "DATA_COLLECTION" : 3,
           "MAP_AND_PICKUP" : 4,
           "MULTIAGENT_PICKUP" : 5,
           "PATH_EFFICIENCY_TRACKER" : 6,
           "MAP_AND_SHOW_PRM" : 7,
    }

    # run only the multi-agent part of the program
    PASSENGER_PICKUP = 0
    # agent moves randomly using the PRM
    RANDOM_NAV = 1
    # only run mapping
    MAP_ONLY = 2
    # run data collection agent, useful for visualizing the prm
    DATA_COLLECTION = 3
    # run mapping and multi-agent
    MAP_AND_PICKUP = 4

    MULTIAGENT_PICKUP = 5

    # track path efficiency for multi-agent
    PATH_EFFICIENCY_TRACKER = 6
    # map, and use map to generate prm
    MAP_AND_SHOW_PRM = 7

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

        # the obstacles the car *thinks* exist
        self.obstacleBeliefs = self.obstacles[:]

        
        self.mode = World.options[sys.argv[1]]

        self.carSize = (20, 20)
        self.kdtreeStart = (0.45 * self.displayWidth, 0.8 * self.displayWidth)
        self.prm = PRM(self)
        self.dirInput = 0   # 1 if up-arrow key, -1 if down-arrow key, 0 if no input
        self.rotInput = 0   # 1 if left-arrow key, -1 if right-arrow key, 0 if no input


        self.cars = list()
        self.frames = 0
        self.frameRate = 60

        ###########################################################################

    # sample integer coordinates from the world
    def sampleInt(self):
        point = (random.randint(0, self.displayWidth), random.randint(0, self.displayHeight))
        for obstacle in self.obstacles + self.obstacleBeliefs:
            if obstacle.colliderect((point[0] - self.carSize[0] / 2.,
                point[1] - self.carSize[1] / 2., self.carSize[0], self.carSize[1])):
                return self.sampleInt()
        return point

    def initPassengerPickup(self):
        self.customers = Customers(self)
        self.numCars = 5
        for i in range(20):
            self.customers.newCustomer(self)
        for i in range(self.numCars):
            while True:
                xy = (numpy.random.randint(0, self.displayWidth), numpy.random.randint(0, self.displayHeight))
                dobreak = True
                for obstacle in self.obstacles:
                    if obstacle.collidepoint(xy):
                        dobreak = False
                        break
                if dobreak:
                    self.cars.append(CustomerMultiAgent(xy[0], xy[1], self, i, self.customers))
                    self.cars[len(self.cars) - 1].prm = self.prm
                    break
        
    def initDataCollection(self):
        self.cars = [DataCollectionAgent(0.45 * self.displayWidth, 0.8 * self.displayWidth, self, 0)]
        self.numCars = 1
        self.prm = PRM(self)
        self.cars[0].prm = self.prm

    def initRandom(self):
        self.cars = [NavigationAgent(0.45 * self.displayWidth, 0.8 * self.displayWidth, self, 0)]
        self.numCars = 1
        self.cars[0].prm = self.prm


    def multiAgentPickup(self):
        self.initPassengerPickup()
        endpts = dict()
        startpts = dict()
        for cust in self.customers.waitingCustomers:
            endpts[cust["endCoords"]] = cust["numCustomer"]
            startpts[cust["startCoords"]] = cust["numCustomer"]
        
        clusterAgent = KMeansClusteringAgent(self.cars, self.customers, self)

        clusterAgent.KMeans()
        paths = clusterAgent.getPaths()

        while len(self.customers.waitingCustomers) > 0 or len(self.customers.drivingCustomers) > 0:
            for event in pygame.event.get():
                pass
            self.screen.fill((255, 255, 255))
            for car in self.cars:
                if not car.currentPath and len(paths[car.IDnumber]) > 0:
                    print paths
                    nextpt = paths[car.IDnumber].pop(0)
                    car.setPath(car.xy, nextpt, self)
                elif car.currentPath and car.i >= len(car.currentPath) - 1:
                    if car.endPoints:
                        print car.endPoints
                        if car.endPoints[1] in endpts:
                            print "dropping off"
                            self.customers.finishedRide(self, endpts[car.endPoints[1]])
                        elif car.endPoints[1] in startpts:
                            print "picking up"
                            self.customers.pickupCustomer(self, startpts[car.endPoints[1]])
                    if(len(paths[car.IDnumber]) > 0):
                        print paths
                        nextpt = paths[car.IDnumber].pop(0)
                        car.setPath(car.xy, nextpt, self)
                car.update(self)
                self.customers.update(self)
                self.clock.tick(self.frameRate)
            
            for obstacle in self.obstacles:
                obstacle.update(self)
            
            pygame.display.update()

    def randomAgentPickup(self):
        self.initPassengerPickup()
        endpts = dict()
        startpts = dict()
        for cust in self.customers.waitingCustomers:
            endpts[cust["endCoords"]] = cust["numCustomer"]
            startpts[cust["startCoords"]] = cust["numCustomer"]
        
        randomAgent = RandomMultiAgent(self.cars, self.customers, self)

        randomAgent.getClusters()
        paths = randomAgent.getPaths()

        while len(self.customers.waitingCustomers) > 0 or len(self.customers.drivingCustomers) > 0:
            for event in pygame.event.get():
                pass
            self.screen.fill((255, 255, 255))
            for car in self.cars:
                if not car.currentPath and len(paths[car.IDnumber]) > 0:
                    print paths
                    nextpt = paths[car.IDnumber].pop(0)
                    car.setPath(car.xy, nextpt, self)
                elif car.currentPath and car.i >= len(car.currentPath) - 1:
                    if car.endPoints:
                        print car.endPoints
                        if car.endPoints[1] in endpts:
                            print "dropping off"
                            self.customers.finishedRide(self, endpts[car.endPoints[1]])
                        elif car.endPoints[1] in startpts:
                            print "picking up"
                            self.customers.pickupCustomer(self, startpts[car.endPoints[1]])
                    if(len(paths[car.IDnumber]) > 0):
                        print paths
                        nextpt = paths[car.IDnumber].pop(0)
                        car.setPath(car.xy, nextpt, self)
                car.update(self)
                self.customers.update(self)
                self.clock.tick(self.frameRate)
            
            for obstacle in self.obstacles:
                obstacle.update(self)
            
            pygame.display.update()
            

    def initPathEfficiencyTracker(self):
        self.customers = Customers(self)
        self.numCars = 10
        self.cars = [CustomerAgent(0.45 * self.displayWidth, 0.8 * self.displayWidth, self, i) for i in range(self.numCars)]
        for car in self.cars:
            car.prm = self.prm
        self.efficiencyTracker = EfficiencyTracker(self.cars, self)
        self.efficiencyTracker.getNtrials(100)


    def mapWorld(self, maxCount = 10000):

        self.cars = [MappingAgent(0.45 * self.displayWidth, 0.8 * self.displayWidth, self, 0)]
        self.cars[0].prm = self.prm

        count = 0
        while count < maxCount:
            for event in pygame.event.get():
                pass
            count += 1
            self.screen.fill((255, 255, 255))
            for car in self.cars:
                if car.i >= len(car.currentPath) - 1:
                    if car.endPoints:
                        car.setPath(car.endPoints[1], car.prm.sample(self), self)
                    else:
                        car.setPath(car.prm.sample(self), car.prm.sample(self), self)
                car.update(self)
            # redraw all the obstacles
            for obstacle in self.obstacles:
                obstacle.update(self)
            # update the screen
            pygame.display.update()
            self.clock.tick(self.frameRate)
        self.cars[0].buildMap()
        self.cars[0].thresh(0.2)
        self.cars[0].drawMap(self)
        self.obstacleCorners = self.cars[0].getObstacles(self)
        self.obstacleBeliefs = self.obstacles[:4]
        for i in range(0, len(self.obstacleCorners), 2):
            x = self.obstacleCorners[i][0]
            y = self.obstacleCorners[i][1]
            width = abs(self.obstacleCorners[i + 1][0] - x)
            height = abs(self.obstacleCorners[i + 1][1] - y)
            self.obstacleBeliefs.append(Obstacle(x, y, width, height, (0, 0, 0)))

    # main game function
    def run(self):
        if self.mode == World.MAP_ONLY or self.mode == World.MAP_AND_PICKUP or self.mode == World.MAP_AND_SHOW_PRM:
            self.mapWorld(2000)
        if self.mode == World.PASSENGER_PICKUP or self.mode == World.MAP_AND_PICKUP:
            self.randomAgentPickup()
        if self.mode == World.DATA_COLLECTION or self.mode == World.MAP_AND_SHOW_PRM:
            if self.mode == World.MAP_AND_SHOW_PRM:
                self.obstacles = self.obstacles[:4] + self.obstacles[10:]
            self.initDataCollection()
        if self.mode == World.RANDOM_NAV:
            self.initRandom()

        if self.mode == World.MULTIAGENT_PICKUP:
            self.multiAgentPickup()

        if self.mode == World.PATH_EFFICIENCY_TRACKER:
            self.initPathEfficiencyTracker()
        ################## some of main loop and some code in __init__ relating to pygame from https://pythonprogramming.net/pygame-python-3-part-1-intro/#########################

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
                    if event.key == pygame.K_p and (self.mode == World.PASSENGER_PICKUP or self.mode == World.MAP_AND_PICKUP or self.mode == World.PATH_EFFICIENCY_TRACKER):
                        self.customers.newCustomer(self)
                        self.customers.newCustomer(self)
                        self.customers.newCustomer(self)
                        self.customers.newCustomer(self)
                        self.customers.newCustomer(self)
                    if event.key == pygame.K_r and self.mode == World.PATH_EFFICIENCY_TRACKER:
                        self.efficiencyTracker.getEfficiency()
                    # clear all waiting customers
                    if event.key == pygame.K_c and (self.mode == World.PASSENGER_PICKUP or self.mode == World.MAP_AND_PICKUP):
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

            for car in self.cars:
                if self.mode == World.PASSENGER_PICKUP or self.mode == World.MAP_AND_PICKUP or self.mode == World.PATH_EFFICIENCY_TRACKER:
                    # print car.i
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
                elif self.mode == World.RANDOM_NAV:
                    if car.i >= len(car.currentPath) - 1:
                        if car.endPoints:
                            car.setPath(car.endPoints[1], car.prm.sample(self), self)
                        else:
                            car.setPath(car.prm.sample(self), car.prm.sample(self), self)
                car.update(self)
                # redraw all the obstacles
            for obstacle in self.obstacles:
                obstacle.update(self)

            for obstacle in self.obstacleBeliefs:
                obstacle.update(self)

            # testing efficiency ratings
            # print(self.cars[0].distanceTraveled)

            if self.mode == World.PASSENGER_PICKUP or self.mode == World.MAP_AND_PICKUP or self.mode == World.PATH_EFFICIENCY_TRACKER:
                self.customers.update(self)

            pygame.display.update()
        ###########################################################################
            
            # try to run at 60 frames per second (or something, not totally sure)
            self.clock.tick(self.frameRate)
        pygame.quit()
        quit()




