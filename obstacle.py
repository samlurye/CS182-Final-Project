import pygame
import math

class Obstacle(pygame.Rect):

    TOPLEFT = 0
    TOPRIGHT = 1
    BOTTOMRIGHT = 2
    BOTTOMLEFT = 3

    def __init__(self, x, y, width, height):
        pygame.Rect.__init__(self, x, y, width, height)
        self.corners = [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height)
        ]

    def update(self, world):
        pygame.draw.rect(world.screen, (0, 0, 255), self)

    def collidepoint(self, point):
        return point[0] >= self.corners[Obstacle.TOPLEFT][0] - 5 and point[1] >= self.corners[Obstacle.TOPLEFT][1] - 5 and \
                point[0] <= self.corners[Obstacle.BOTTOMRIGHT][0] + 5 and point[1] <= self.corners[Obstacle.BOTTOMRIGHT][1] + 5


