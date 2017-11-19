import pygame
import math

def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

class World:

    def __init__(self):
        pygame.init()
        self.displayWidth = 800
        self.displayHeight = 800
        self.screen = pygame.display.set_mode((self.displayWidth, self.displayHeight))
        pygame.display.set_caption('CS182 Final Project')   # text at the top of the window
        self.clock = pygame.time.Clock()
        self.isRunning = True
        self.car = Car(self.displayWidth * 0.45, self.displayHeight * 0.8)
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
        self.dirInput = 0   # 1 if up-arrow key, -1 if down-arrow key, 0 if no input
        self.rotInput = 0   # 1 if left-arrow key, -1 if right-arrow key, 0 if no input

    def run(self):
        # main game loop
        while self.isRunning:
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
            # move the car and check for collisions
            self.car.update(self)
            # redraw all the obstacles
            for obstacle in self.obstacles:
                obstacle.update(self) 
            # update the screen
            pygame.display.update()
            # try to run at 60 frames per second (or something, not totally sure)
            self.clock.tick(60)
        pygame.quit()
        quit()

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

class Obstacle(pygame.Rect):

    def __init__(self, x, y, width, height):
        pygame.Rect.__init__(self, x, y, width, height)

    def update(self, world):
        pygame.draw.rect(world.screen, (0, 0, 255), self)

if __name__ == "__main__":
    w = World()
    w.run()




