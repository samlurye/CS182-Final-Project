import pygame
import math
from sensor import SensorModel, Sensor
from PRM import *
import random
import time
import numpy
import car
import customer
import sys


class EfficiencyTracker:

	def __init__(self, cars, world):
		self.totalPathLengths = 0
		self.cars = cars
		self.world = world

	def getNtrials(self, n):
		for _ in range(n):
			self.world.customers.newCustomer(self.world)
		# time.sleep(1)
		# self.getEfficiency()


		# for car in self.cars:
		# 	self.totalPathLengths += car.distanceTraveled
		# 	print("cars:") + str(car.distanceTraveled)
		# print("Total path length of customer trips")
		# print("WORKING")
		# print self.totalPathLengths
	def getEfficiency(self):
		distanceTraveledSoFar = 0
		print("")
		for car in self.cars:
			distanceTraveledSoFar += car.distanceTraveled
			print("car #") + str(car.IDnumber + 1) + ": " + str(car.distanceTraveled)
		print("efficiency: ") + str(distanceTraveledSoFar)


