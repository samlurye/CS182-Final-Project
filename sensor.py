import pygame
import math
from obstacle import Obstacle
import numpy as np
import scipy.stats

class Sensor:

    NORMALCDF = scipy.stats.norm.cdf

    def __init__(self, direction):
        # sensing distance
        self.maxDist = 400
        # rotation angle with respect to car's direction
        self.direction = math.radians(direction)
        # line that represents the beam of the sensor
        self.beam = None
        # starting point of beam (i.e., the car)
        self.start = (0, 0)
        # end point of beam
        self.end = (0, 0)
        # standard deviation (or maybe variance, need to check) of normally distributed error of sensor
        self.noise = 10

    # update sensor graphics
    def update(self, world):
        self.start = world.car.center()
        self.end = self.getEnd(self.start, self.getHeading(world))
        pygame.draw.line(world.screen, (0, 255, 0), self.start, self.end, 2)
        self.beam = (self.start[0], self.start[1], self.end[0], self.end[1])

    # returns (exact sensor reading, noisy sensor reading) given a position and orientation
    # orientation is always taken from car
    # if particle is not None, position is taken from particle
    def getReading(self, world):
        start = self.start
        end = self.end
        beam = self.beam
        nearestHit = None
        distToNearestHit = float("inf")
        # find the first point of collision of the sensor's beam
        for obstacle in world.obstacles:
            hit = obstacle.collideline(beam)
            if hit:
                distToHit = dist(hit, start)
                if distToHit < distToNearestHit and distToHit < self.maxDist:
                    nearestHit = hit
                    distToNearestHit = distToHit
        noisyNearestHit = None
        if nearestHit:
            noisyNearestHit = self.addNoise(nearestHit, distToNearestHit, world)
            pygame.draw.rect(world.screen, (255, 0, 0), (noisyNearestHit[0] - 5, noisyNearestHit[1] - 5, 10, 10))
        return nearestHit, noisyNearestHit

    def addNoise(self, point, distToPoint, world):
        scale = np.random.normal(0, self.noise)
        noise = point[0] + scale / self.maxDist * (self.end[0] - self.start[0]), point[1] \
                + scale / self.maxDist * (self.end[1] - self.start[1])
        if noise[0] >= 0 and noise[0] <= world.displayWidth and noise[1] >= 0 and noise[1] <= world.displayHeight:
            return noise
        return point

    # get direction of sensor beam
    def getHeading(self, world):
        carHeading = (math.cos(math.radians(world.car.orientation)), math.sin(math.radians(world.car.orientation)))
        return rotateVector(carHeading, self.direction)

    # get endpoint of sensor beam
    def getEnd(self, start, heading):
        return (self.maxDist * heading[0] + start[0], -self.maxDist * heading[1] + start[1])

    # given the expected reading, returns the probability that the noisy reading is within a given window of size 2
    def getEmissionProbability(self, expectedReading, noisyReading):
        diff = math.floor(dist(expectedReading, noisyReading))
        return Sensor.NORMALCDF(diff + 1, 0, self.noise) - Sensor.NORMALCDF(diff - 1, 0, self.noise)


class SensorModel:

    def __init__(self):
        self.sensors = [Sensor(45 * i) for i in range(8)]

    def getReadings(self, world):
        readings = []
        for sensor in self.sensors:
            sensor.update(world)
            readings.append(sensor.getReading(world))
        return readings

    def getSensors(self):
        return self.sensors
    # returns p(all sensor readings | particle position, car orientation, map)
    def getEmissionProbability(self, world, particle):
        emissionProbability = 1
        for sensor in self.sensors:
            expectedReading, noisyReading = sensor.getReading(world, particle)
            if expectedReading and noisyReading:
                emissionProbability *= sensor.getEmissionProbability(expectedReading, noisyReading)
            else:
                emissionProbability = 0.0
        return emissionProbability

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
















