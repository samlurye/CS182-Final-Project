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

    
    # takes in a customer ID number and updates the lists when since the ride is over
    def finishedRide(self, world, customerNumber):
        self.drivingCustomers = [x for x in self.drivingCustomers if x["numCustomer"] != customerNumber]
        self.numServedCustomers += 1

    # moves a customer from the waiting to the driving list
    def pickupCustomer(self, world, customerNumber):

        # gets the passenger's dictionary
        customerToPickup = [x for x in self.waitingCustomers if x[numCustomer] == customerNumber][0]
        self.drivingCustomers.append(customerToPickup)
        self.waitingCustomers.remove(customerToPickup)

    # adds a new, numbered customer to waitingCustomers with a start/end destination
    def newCustomer(self, world):
        # Adds a new customer to the waiting list. Customers are dicts with a number, a start point, and a destination point
        self.waitingCustomers.append({"numCustomer": len(self.waitingCustomers) + len(self.drivingCustomers) + self.numServedCustomers + 1, \
            "startCoords": world.prm.sample(world), "endCoords": world.prm.sample(world)})


    def update(self, world):
    	for customer in self.waitingCustomers:
            startCoords = (int(round(customer["startCoords"][0])), int(round(customer["startCoords"][1])))
            endCoords = (int(round(customer["endCoords"][0])), int(round(customer["endCoords"][1])))
            pygame.draw.circle(world.screen, (0, 255, 0), startCoords, 6)
            pygame.draw.circle(world.screen, (255, 0, 0), endCoords, 6)
            world.screen.blit(self.font.render("Passenger " + str(customer["numCustomer"]) + " pickup", True, (0,0,0)), startCoords)
            world.screen.blit(self.font.render("Passenger " + str(customer["numCustomer"]) + " dropoff", True, (0,0,0)), endCoords)
        for customer in self.drivingCustomers:
            endCoords = (int(round(customer["endCoords"][0])), int(round(customer["endCoords"][1])))
            pygame.draw.circle(world.screen, (0, 0, 255), endCoords, 6)
            world.screen.blit(self.font.render("Passenger " + str(customer["numCustomer"]), True, (0,0,0)), endCoords)
