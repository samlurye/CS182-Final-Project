import pygame
import math
from sensor import SensorModel

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
        self.sensorModel.getReadings(world)

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













