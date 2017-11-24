import pygame
import math
from obstacle import Obstacle
import numpy as np

class Sensor:

    def __init__(self, direction):
        self.maxDist = 400
        self.direction = math.radians(direction)
        self.beam = None
        self.start = (0, 0)
        self.end = (0, 0)
        self.noise = 10

    def update(self, world):
        self.start = world.car.center()
        carHeading = (math.cos(math.radians(world.car.orientation)), math.sin(math.radians(world.car.orientation)))
        sensorHeading = rotateVector(carHeading, self.direction)
        self.end = (self.maxDist * sensorHeading[0] + self.start[0], -self.maxDist * sensorHeading[1] + self.start[1])
        self.beam = pygame.draw.line(world.screen, (0, 255, 0), self.start, self.end, 2)

    def getReading(self, world):
        nearestHit = None
        distToNearestHit = float("inf")
        for obstacle in world.obstacles:
            if self.beam.colliderect(obstacle):
                for i in range(len(obstacle.corners)):
                    hit = getIntersection(self.start, self.end, obstacle.corners[i], obstacle.corners[(i + 1) % 4])
                    if hit:
                        distToHit = dist(hit, self.start)
                        if obstacle.collidepoint(hit) and distToHit < distToNearestHit:
                                nearestHit = hit
                                distToNearestHit = distToHit
        if nearestHit:
            nearestHit = self.addNoise(nearestHit, distToNearestHit)
            pygame.draw.rect(world.screen, (255, 0, 0), (nearestHit[0] - 5, nearestHit[1] - 5, 10, 10))
        return nearestHit

    def addNoise(self, point, distToPoint):
        scale = np.random.normal(0, self.noise)
        return point[0] + scale / self.maxDist * (self.end[0] - self.start[0]), point[1] \
                + scale / self.maxDist * (self.end[1] - self.start[1])


class SensorModel:

    def __init__(self):
        self.sensors = [Sensor(45 * i) for i in range(8)]

    def getReadings(self, world):
        for sensor in self.sensors:
            sensor.update(world)
            hits = sensor.getReading(world)

### https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines-in-python ####
def line(p1, p2):
    A = (p1[1] - p2[1])
    B = (p2[0] - p1[0])
    C = (p1[0]*p2[1] - p2[0]*p1[1])
    return A, B, -C

def intersection(L1, L2):
    D  = L1[0] * L2[1] - L1[1] * L2[0]
    Dx = L1[2] * L2[1] - L1[1] * L2[2]
    Dy = L1[0] * L2[2] - L1[2] * L2[0]
    if D != 0:
        x = float(Dx) / D
        y = float(Dy) / D
        return x,y
    else:
        return False
#####################################################################################################################

def getIntersection(p1, p2, p3, p4):
    return intersection(line(p1, p2), line(p3, p4))

def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def rotateVector(v, angle):
    return math.cos(angle) * v[0] - math.sin(angle) * v[1], math.sin(angle) * v[0] + math.cos(angle) * v[1]
















