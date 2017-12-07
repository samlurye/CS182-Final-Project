import pygame
import math
from sensor import SensorModel, Sensor
from PRM import *
import random
import time
import numpy
import sys

################## https://www.pygame.org/wiki/RotateCenter #########################
def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image
###########################################################################

class Car:

    def __init__(self, x, y, world, IDnum):
        self.orig_image = pygame.transform.scale(pygame.image.load('car.png'), (20, 20)) # original, unrotated car image
        self.image = self.orig_image.copy()     # image that actually gets rendered for the user
        self.size = self.image.get_size()       # dimensions of the user 
        self.xy = (x, y)                        # xy position of the user
        self.orientation = 90                   # rotational orientation of the user (pygame uses degrees, dumb...)
        self.speed = 0                          # magnitude of the velocity of the car (can go negative, though, which means car is moving in reverse)
        self.velocity = (0, 0)                  # velocity vector of the car
        self.maxSpeed = 7                       # maximum speed attainable by car
        self.angvel = 2.5                       # rotation speed of car
        self.acc = 4                            # acceleration of car
        self.drag = .6                          # drag force exerted on car
        self.dt = 0.1                           # time step
        self.sensorModel = SensorModel()
        # new stuff to keep track of car ID
        self.IDnumber = IDnum
        self.font = pygame.font.SysFont('Arial', 20)
        

    def getVelocity(self, dirInput):
        # update speed according to forces exerted on car
        self.speed += -self.drag * self.speed * self.dt + dirInput * self.acc * self.dt
        # clip speed to -maxSpeed < speed < maxSpeed
        self.speed = max(min(self.speed, self.maxSpeed), -self.maxSpeed)
        # return the velocity vector
        return self.speed * math.cos(math.radians(self.orientation)), -self.speed * math.sin(math.radians(self.orientation))

    def update(self, world):
        if world.rotInput:
            # rotate the car
            self.orientation = (self.orientation + world.rotInput * self.angvel) % 360
            self.image = rot_center(self.orig_image, self.orientation + world.rotInput * self.angvel - 90)
        # check for collisions and update velocity appropriately
        if not self.checkCollisions(world):
            self.velocity = self.getVelocity(world.dirInput)
        # move the car
        self.xy = (self.xy[0] + self.velocity[0], self.xy[1] + self.velocity[1])
        # draw car to screen
        world.screen.blit(self.image, self.xy)
        

    def checkCollisions(self, world):
        collided = False
        # if car collides with any of the obstacles, reverse its velocity
        for obstacle in world.obstacles:
            if obstacle.colliderect((self.xy[0], self.xy[1], self.size[0], self.size[1])):
                self.velocity = (-self.velocity[0], -self.velocity[1])
                self.speed *= -1
                collided = True
        return collided

    def center(self):
        return self.xy[0] + self.size[0] / 2., self.xy[1] + self.size[1] / 2.

    def normalize(self, dist):
        tot = sum(dist.values())
        for i in dist.keys():
            dist[i] = dist[i] / tot

class MappingAgent(Car):

    """Human-controlled car that maps using sensor data"""

    def __init__(self, x, y, world, idnum):
        Car.__init__(self, x, y, world, idnum)
        self.displayWidth = world.displayWidth
        self.displayHeight = world.displayHeight
        self.map = self.blankMap()
        self.occupancyGrid = self.blankOccupancyGrid()
        self.obstacleCorners = []
        self.prm = None
        self.currentPath = []
        self.endPoints = None
        self.i = 0
        self.pathLength = 0
        self.mode = 0

    def blankMap(self):
        dist = dict()
        for i in range(self.displayWidth):
            for j in range(self.displayHeight):
                dist[(i, j)] = 0.0
        return dist

    def observe(self, world):
        readings = self.sensorModel.getReadings(world)
        for read in readings:
            if read[1] != None:
                pos = [self.xy[0], self.xy[1]]
                end = (round(read[1][0]), round(read[1][1]))
                if end[0] >= 0 and end[0] <= self.displayWidth and end[1] >= 0 and end[1] <= self.displayHeight:
                    self.occupancyGrid[end]["hit"] += 1
                slope = 0
                if pos[0] - end[0] == 0:
                    if pos[1] < end[1]:
                        slope = 1
                    else:
                        slope = -1
                else:
                    slope = float(pos[1] - end[1]) / (pos[0] - end[0])
                while abs(pos[0] - end[0]) > 1 and abs(pos[1] - end[1]) > 1:
                    if pos[0] >= 0 and pos[0] <= self.displayWidth and pos[1] >= 0 and pos[1] <= self.displayHeight:
                        self.occupancyGrid[(round(pos[0]), round(pos[1]))]["miss"] += 1
                    if end[0] < pos[0]:
                        pos[0] -= 1
                        pos[1] += slope * -1
                    elif end[0] > pos[0]:
                        pos[0] += 1
                        pos[1] += slope
                    else:
                        pos[1] += slope

    def blankOccupancyGrid(self):
        occupancyGrid = dict()
        for i in range(self.displayWidth + 1):
            for j in range(self.displayHeight + 1):
                occupancyGrid[(i, j)] = dict(hit = 0, miss = 0)
        return occupancyGrid

    def buildMap(self):
        print "building"
        for key in self.map.keys():
            if self.occupancyGrid[key]["hit"] + self.occupancyGrid[key]["miss"]:
                self.map[key] = float(self.occupancyGrid[key]["hit"]) / (self.occupancyGrid[key]["hit"] + self.occupancyGrid[key]["miss"])
            else:
                self.map[key] = 0

    def thresh(self, alpha):
        print "thresh"
        for key in self.map.keys():
            if self.map[key] < alpha:
                self.map[key] = 0.0
            else:
                self.map[key] = 1.0

    def drawMap(self, world):
        print "drawing"
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    return
            for cell in self.map.keys():
                if self.map[cell] == 1.0:
                    pygame.draw.rect(world.screen, (0,0,0), (cell[0], cell[1], 2, 2))
            pygame.display.update()
            world.clock.tick(20)

    def extractBorders(self):
        points = list()
        for cell in self.map.keys():
                if(self.map[cell] == 1.0):
                    points.append(cell)
        return points

    def generateRandomMeans(self, width, height, k = 15):
        means = list()
        for i in range(k):
            means.append((numpy.random.randint(0, width), numpy.random.randint(0, height)))
        return means

    def dist(x1, x2, y1, y2):
        return sqrt((x1 - y1) ** 2 + (x2 - y2) ** 2)

    def iterateMeans(self, clusters, means):
        for c in range(len(clusters)):
            cluster = clusters[c]
            if not len(cluster) == 0:
                l = len(cluster)
                means[c] =  ((sum([point[0] for point in cluster])/l, \
                              sum([point[1] for point in cluster])/l ))
        change = False

        appendList = [[] for i in range(len(clusters))]
        for c in range(len(clusters)):
           
            for point in clusters[c]:

                minIndex = c
                minDist = dist(point, means[c])
                for m in range(len(means)):

                    d = dist(point, means[m])
                    if d < minDist:
                        minIndex = m
                        minDist = d
                if minIndex != c:
                    change = True
                    appendList[minIndex].append(point)
                    clusters[c].remove(point)
        if not change:
            return clusters
        else:
            for i in range(len(appendList)):
                clusters[i].extend(appendList[i])
            return self.iterateMeans(clusters, means)

    def kMeans(self, points, width, height):
        means = self.generateRandomMeans(width, height)
        clusters = [[] for i in range(len(means))]
        points = self.extractBorders()
        for point in points:
            minIndex = 0
            minDist = sys.maxint
            for m in range(len(means)):
                d = dist(point, means[m])
                if d < minDist:
                    minIndex = m
                    minDist = d
            clusters[minIndex].append(point)
        return self.iterateMeans(clusters, means)

    def corners(self, obstacles):
        for obstacle in obstacles:
            obstacle = sorted(obstacle, key=lambda x:x[0])
            obstacle = sorted(obstacle, key=lambda x:x[1])
            if len(obstacle):
                obstacle = sorted(obstacle, key=lambda x:x[0])
                left = obstacle[0][0]
                right = obstacle[len(obstacle) - 1][0]
                obstacle = sorted(obstacle, key=lambda x:x[1])
                top = obstacle[0][1]
                bottom = obstacle[len(obstacle) - 1][1]
                self.obstacleCorners.extend([(left, top), (right, bottom)])
        return self.obstacleCorners

    def getObstacles(self, world):
        borders = self.extractBorders()
        means = self.kMeans(borders, self.displayWidth, self.displayHeight)
        print len(means)
        corners = self.corners(means)
        """for corner in corners:
            pygame.draw.circle(world.screen, (255,0, 0), (int(corner[0]), int(corner[1])), 10)"""
        pygame.display.update()
        self.corners = corners
        return corners

    def update(self, world):
        # this is going to give you another merge conflict but please leave it as is,
        # otherwise we get weird alignment issues with the sensor and the car during mapping
        pygame.draw.circle(world.screen, (255, 0, 0), (int(round(self.xy[0])), int(round(self.xy[1]))), 10)
        self.observe(world)
        if self.i < len(self.currentPath) - 1:
            self.xy = self.currentPath[self.i + 1]
            self.pathLength += dist(self.xy, self.currentPath[self.i])
            self.i += 1


    def setPath(self, start, end, world):
        self.endPoints = start, end
        self.currentPath = self.prm.getPath(self.endPoints[0], self.endPoints[1], world)
        self.i = 0
        self.pathLength = 0


class NavigationAgent(Car):

    """Agent that can navigate the world automatically using a PRM"""

    def __init__(self, x, y, world, IDnum):
        Car.__init__(self, x, y, world, IDnum)
        self.prm = None
        self.currentPath = []
        self.endPoints = None
        self.i = 0
        self.pathLength = 0
        self.distanceTraveled = 0 

    def update(self, world):
        if self.currentPath and self.i < len(self.currentPath) - 1:
            self.xy = self.currentPath[self.i + 1]
            self.pathLength += dist(self.xy, self.currentPath[self.i])
            self.i += 1
        pygame.draw.circle(world.screen, (255, 0, 0), (int(round(self.xy[0])), int(round(self.xy[1]))), 10)
        world.screen.blit(self.font.render("Car" + str(self.IDnumber + 1), True, (20,0,0)), (int(round(self.xy[0])), int(round(self.xy[1]))))

    # set a path for the car to follow
    def setPath(self, start, end, world):
        self.endPoints = start, end
        self.currentPath = self.prm.getPath(self.endPoints[0], self.endPoints[1], world)
        self.i = 0
        self.pathLength = 0

class CustomerAgent(NavigationAgent):

    def __init__(self, x, y, world, IDnum, customers):
        NavigationAgent.__init__(self, x, y, world, IDnum)
        self.customers = customers

    # takes in a MIDDLE
    def setPath(self, start, end, world):
        NavigationAgent.setPath(self, start, end, world)

        # length of two lines in pathway
        dist1 = math.hypot(start[0] - end[0], start[1] - end[1])
        self.distanceTraveled += (dist1)
        # print(self.distanceTraveled)


class DataCollectionAgent(NavigationAgent):

    """Automatically collects data on PRM vs RRT"""

    def __init__(self, x, y, world, IDNum):
        NavigationAgent.__init__(self, x, y, world, IDNum)
        self.mode = 0

    def update(self, world):
        if self.i < len(self.currentPath) - 1:
            self.xy = self.currentPath[self.i + 1]
            self.pathLength += dist(self.xy, self.currentPath[self.i])
            self.i += 1
        else:
            if len(self.currentPath) > 0:
                if self.mode == 1:
                    print "PRM L " + str(self.pathLength) + "\n"
                else:
                    print "RRT L " + str(self.pathLength) + "\n"
            if self.mode == 0:
                self.endPoints = (self.prm.sample(world), self.prm.sample(world))
                print "PRM P " + str(self.endPoints[0][0]) + " " + str(self.endPoints[0][1]) + " " + \
                        str(self.endPoints[1][0]) + " " + str(self.endPoints[1][1])
                start = time.clock()
                self.currentPath = self.prm.getPath(self.endPoints[0], self.endPoints[1], world)
                end = time.clock()
                print "PRM T " + str(end - start)
                self.mode = 1
            elif self.mode == 1:
                print "RRT P " + str(self.endPoints[0][0]) + " " + str(self.endPoints[0][1]) + " " + \
                        str(self.endPoints[1][0]) + " " + str(self.endPoints[1][1])
                start = time.clock()
                self.currentPath = RRT(self.endPoints[0], self.endPoints[1]).run(world)
                end = time.clock() 
                print "RRT T " + str(end - start)
                self.mode = 0
            self.i = 0
            self.pathLength = 0
        for p1 in self.prm.connections:
            for p2 in self.prm.connections[p1]:
                pygame.draw.line(world.screen, (0, 0, 0), p1, p2)
        pygame.draw.circle(world.screen, (255, 0, 0), (int(round(self.xy[0])), int(round(self.xy[1]))), 10)













