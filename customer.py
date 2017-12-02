import pygame
import random
import time
import numpy
from PRM import *

class Customers:

    def __init__(self, world):
        # can be done with len(self.waitingCustomers) etc
    	# self.numWaitingCustomers = 0
        # self.numDrivingCustomers = 0
        self.numServedCustomers = 0
        self.waitingCustomers = []
        self.drivingCustomers = []
        self.font = pygame.font.SysFont('Arial', 14)



	# secs = 0
 #    	# Loop until we reach 20 seconds running
 #    while secs != 20:
 #        # Sleep for a second
 #        time.sleep(1)
 #       	 secs += 1
             #make a new passenger

    # moves a customer from the waiting to the driving list
    def pickupCustomer(self, world, customerNumber):

        # gets the passenger's dictionary
        customerToPickup = [x for x in self.waitingCustomers if x[numCustomer] == customerNumber][0]
        self.drivingCustomers.append(customerToPickup)
        self.waitingCustomers.remove(customerToPickup)


    # takes in a customer ID number and updates the lists when since the ride is over
 	def finishedRide(self, world, customerNumber):
 		self.drivingCustomers = [x for x in self.drivingCustomers if x[numCustomer] != customerNumber]
 		self.numServedCustomers += 1



    # adds a new, numbered customer to waitingCustomers with a start/end destination
    def newCustomer(self, world):
		
    	# gets viable starting coords (terrible I know)
		# startCoords = (random.random() * world.displayWidth, random.random() * world.displayHeight)
		# haveValidStartCoords = True
		# for obstacle in world.obstacles:
  #           if obstacle.collidepoint(startCoords):
  #           	haveValidStartCoords = False
  #       while not haveValidStartCoords:
  #       	startCoords = (random.random() * world.displayWidth, random.random() * world.displayHeight)
		# 	haveValidStartCoords = True
		# 	for obstacle in world.obstacles:
  #           	if obstacle.collidepoint(startCoords):
  #           		haveValidStartCoords = False

  #       # gets viable end coords (terrible I know)
  #       endCoords = (random.random() * world.displayWidth, random.random() * world.displayHeight)
		# haveValidEndCoords = True
		# for obstacle in world.obstacles:
  #           if obstacle.collidepoint(endCoords):
  #           	haveValidEndCoords = False
  #       while not haveValidEndCoords:
  #       	endCoords = (random.random() * world.displayWidth, random.random() * world.displayHeight)
		# 	haveValidEndCoords = True
		# 	for obstacle in world.obstacles:
  #           	if obstacle.collidepoint(EndCoords):
  #           		haveValidEndCoords = False


        # self.waitingCustomers.append({"numCustomer": self.numCustomersServed + 1, "startCoords": startCoords, "endCoords": endCoords})

        # Adds a new customer to the waiting list. Customers are dicts with a number, a start point, and a destination point
        self.waitingCustomers.append({"numCustomer": len(self.waitingCustomers) + len(self.drivingCustomers) + self.numServedCustomers + 1, \
            "startCoords": world.prm.sample(world), "endCoords": world.prm.sample(world)})


    def update(self, world):
    	for customer in self.waitingCustomers:
            startCoords = (int(round(customer["startCoords"][0])), int(round(customer["startCoords"][1])))
            endCoords = (int(round(customer["endCoords"][0])), int(round(customer["endCoords"][1])))
            pygame.draw.circle(world.screen, (255, 0, 0), startCoords, 6)
            pygame.draw.circle(world.screen, (0, 255, 0), endCoords, 6)
            world.screen.blit(self.font.render("Passenger " + str(customer["numCustomer"]), True, (0,0,0)), startCoords)
            world.screen.blit(self.font.render("Passenger " + str(customer["numCustomer"]), True, (0,0,0)), endCoords)
