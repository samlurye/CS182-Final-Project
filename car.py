import pygame
import math
from sensor import SensorModel, Sensor
import random
import time
import numpy

################## DON'T FORGET TO CITE THIS CODE #########################
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

    def __init__(self, x, y):
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
            self.orientation += world.rotInput * self.angvel
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

    def __init__(self, x, y, world):
        Car.__init__(self, x, y)
        self.numParticles = 5000
        self.particles = self.generateNParticles(self.numParticles, world)
        self.displayWidth = world.displayWidth
        self.displayHeight = world.displayHeight
        self.map = self.blankMap()
        self.occupancyGrid = self.blankOccupancyGrid()
        self.obstacleCorners = []


    # generates n uniformly distributed particles
    def generateNParticles(self, n, world):
        particles = []
        for i in range(n):
            point = (random.randint(0, world.displayWidth - 1), random.randint(0, world.displayHeight - 1))
            particles.append(point)
        return particles

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
        for key in self.map.keys():
            self.map[key] = float(self.occupancyGrid[key]["hit"]) / (self.occupancyGrid[key]["hit"] + self.occupancyGrid[key]["miss"])

    def thresh(self, alpha):
        for key in self.map.keys():
            if self.map[key] < alpha:
                self.map[key] = 0.0
            else:
                self.map[key] = 1.0

    def drawMap(self, world):
        for cell in self.map.keys():
            if self.map[cell] == 1.0:
                pygame.draw.rect(world.screen, (0,0,0), (cell[0], cell[1], 1, 1))

    def extractBorders(self):
        points = list()
        for cell in self.map.keys():
            if self.map[cell] == 1.0:
                points.append(cell)

    def generateRandomMeans(self, width, height, k = 10):
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
                means[c] = ((sum(point[0] for point in cluster)/l, \
                             sum(point[1] for point in cluster)/l ))
        change = False

        appendList = [[] for i in range(len(clusters))]
        for c in range(len(clusters)):
            for point in cluster[c]:
                minIndex = c
                minDist = dist(point, means[c])
                for m in range(means):
                    d = dist(point, means[m])
                    if d < minDist:
                        minIndex = m
                        minDist = d
                if minIndex != c:
                    change = True
                    appendList[minIndex] = point
                    clusters[c].pop(point)
        if not change:
            return clusters
        else:
            for i in range(len(appendList)):
                clusters[i].extend(appendList[i])
            self.iterateMeans(clusters, means)

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
        return self.iterateMeans(clusters, means)


    def corners(self, obstacles):
        for obstacle in obstacles:
            obstacle = sorted(obstacle, key=lambda x:x[0])
            obstacle = sorted(obstacle, key=lambda x:x[1])
            self.obstacleCorners.append([obstacle[0], obstacle[len(obstacle) - 1]])





    """
    def updateParticles(self, world):
        newParticles = []
        emissionProbabilities = []
        for i in range(len(self.particles)):
            # update particle according to movement of car
            self.particles[i] = (self.particles[i][0] + self.velocity[0] + random.randint(-5, 5), self.particles[i][1] + self.velocity[1] + random.randint(-5, 5))
            collision = False
            # check for collisions
        
            for obstacle in world.obstacles:
                if obstacle.collidepoint(self.particles[i]):
                    collision = True
                    break

            # if particle didn't collide, find P(sensor readings|particle position)
            if not collision:
                emissionProbabilities.append(self.sensorModel.getEmissionProbability(world, self.particles[i]))
            else:
                emissionProbabilities.append(0)

        # sample new particles
        sumEP = sum(emissionProbabilities)
        emissionProbabilities = [emissionProbabilities[i] / sumEP for i in range(self.numParticles)]
        particleIndices = numpy.random.choice(range(self.numParticles), self.numParticles, True, emissionProbabilities)
        self.particles = [self.particles[particleIndices[i]] for i in range(self.numParticles)]
    
        # draw particles
        for particle in self.particles:
                pygame.draw.rect(world.screen, (0, 0, 0), (particle[0], particle[1], 5, 5))
    """


    def update(self, world):
        Car.update(self, world)
        self.observe(world)
















