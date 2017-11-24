import pygame
import math

class Obstacle(pygame.Rect):

    TOPLEFT = 0
    TOPRIGHT = 1
    BOTTOMRIGHT = 2
    BOTTOMLEFT = 3
    TOP = 4
    BOTTOM = 5
    LEFT = 6
    RIGHT = 7
    COLLISIONSECTORS = [
        set([BOTTOM, BOTTOMRIGHT, RIGHT]),
        set([BOTTOM, BOTTOMLEFT, LEFT]),
        set([TOP, TOPLEFT, LEFT]),
        set([TOP, TOPRIGHT, RIGHT]),
        set([RIGHT, BOTTOMRIGHT, BOTTOM, BOTTOMLEFT, LEFT]),
        set([RIGHT, TOPRIGHT, TOP, TOPLEFT, LEFT]),
        set([TOP, TOPRIGHT, RIGHT, BOTTOMRIGHT, BOTTOM]),
        set([TOP, TOPLEFT, LEFT, BOTTOMLEFT, BOTTOM])
    ]

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

    # check to see if point inside obstacle
    def collidepoint(self, point):
        return point[0] >= self.corners[Obstacle.TOPLEFT][0] and point[1] >= self.corners[Obstacle.TOPLEFT][1] and \
                point[0] <= self.corners[Obstacle.BOTTOMRIGHT][0] and point[1] <= self.corners[Obstacle.BOTTOMRIGHT][1]

    # check if line collides with obstacle
    def collideline(self, line):
        start = line[0], line[1]
        end = line[2], line[3]
        if self.collidepoint(end):
            return True
        return self.getSector(end) in Obstacle.COLLISIONSECTORS[self.getSector(start)]

    # sector/obstacle layout

          #       #
      #0  #   #4  # #1
          #       #
    # # # # # # # # # # #
      #6  # Obst. # #7
          #       #
    # # # # # # # # # # #
      #3  #   #5  #  
          #       # #2
          #       #

    # so if start point of line segment in sector 1 and end point of line segment in sector 5,
    # the line must collide with the obstacle
    
    def getSector(self, point):
        top = self.corners[Obstacle.TOPLEFT][1]
        left = self.corners[Obstacle.TOPLEFT][0]
        bottom = self.corners[Obstacle.BOTTOMRIGHT][1]
        right = self.corners[Obstacle.BOTTOMRIGHT][0]
        if point[0] <= left and point[1] <= top:
            return Obstacle.TOPLEFT
        elif point[0] <= left and point[1] <= bottom:
            return Obstacle.LEFT
        elif point[0] <= left:
            return Obstacle.BOTTOMLEFT
        elif point[0] <= right and point[1] >= bottom:
            return Obstacle.BOTTOM
        elif point[1] >= bottom:
            return Obstacle.BOTTOMRIGHT
        elif point[1] >= top:
            return Obstacle.RIGHT
        elif point[0] >= right:
            return Obstacle.TOPRIGHT
        else:
            return Obstacle.TOP












