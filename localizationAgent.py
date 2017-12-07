import pygame
import math
from sensor import SensorModel
import random
import time
import numpy
from car import Car

class LocalizationAgent(Car):

    """Human-controlled car that localizes using particle filtering"""

    def __init__(self, x, y, world):
        Car.__init__(self, x, y)
        self.sensorModel = SensorModel()
        self.numParticles = 500
        self.particles = self.generateNParticles(self.numParticles, world)

    # generates n uniformly distributed particles
    def generateNParticles(self, n, world):
        particles = []
        for i in range(n):
            success = False
            while not success:
                success = True
                point = (random.random() * world.displayWidth, random.random() * world.displayHeight)
                for obstacle in world.obstacles:
                    if obstacle.collidepoint(point):
                        success = False
                        break
                if success:
                    particles.append(point)
        return particles

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

    def update(self, world):
        Car.update(self, world)
        self.sensorModel.getReadings(world)
        self.updateParticles(world)



        