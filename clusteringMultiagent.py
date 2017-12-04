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


class KMeansClusteringAgent:

	def __init__(self, cars, passengers, world):
		self.means = dict()

		self.clusters = dict()
		self.cars = cars
		self.passengers = passengers
		self.world = world

	def getStartingMeans(self):
		for car in self.cars:
			self.means[car.i] = car.xy

	def euclid(start, end):
		return sqrt((start[0] - end[0])**2 + (start[1] - end[1])**2)

	def dist(mean, passenger):
		return self.euclid(mean, passenger["startCoords"]) + self.euclid(mean, passenger["endCoords"])

	def assignMeans(self):
		for passenger in self.passengers:
			minDist = sys.maxint
			minMean = 0
			for mean in self.means.keys():
				dist = self.dist(self.means[mean], passenger)
				if(dist < minDist):
					minDist = dist
					minMean = mean
			self.clusters[mean].append(passenger)

	def updateMeans(self):
		for mean in self.means.keys():
			x = 0
			y = 0
			for p in self.clusters[mean]:
				x += p["startCoords"][0] + p["endCoords"][0]
				y += p["startCoords"][1] + p["endCoords"][1]
			self.means[mean] = (int(x / (len(self.clusters[mean] * 2))), \
								int(y / (len(self.clusters[mean] * 2))))

	def updateClusters(self):
		swap = False
		updates = dict()
		for cluster in self.clusters.keys():
			for passinger in self.clusters[cluster]:
				minDist = sys.maxint
				minMean = cluster
				for mean in self.means.keys():
					dist = self.dist(self.means[mean], passenger)
					if(dist < minDist):
						minDist = dist
						minMean = mean
				if minMean != cluster:
					swap = True
					updates[minMean].append(passenger)
					self.clusters[cluster].pop(passenger)
		for el in updates.keys():
			self.clusters[el].extend(updates[el])
		return swap

	def KMeans(self):
		self.getStartingMeans()
		self.assignMeans()

		while True:
			self.updateMeans()

			if not self.updateClusters():
				break
		return self.clusters

class Tree:
	def __init__(self, data = None, left = None, right = None):
		self.left = left
		self.right = right
		self.data = data

class AgglomerativeAgent:
	def __init__(self, cars, passengers, world):
		self.means = dict()

		self.clusters = dict()
		self.cars = cars
		self.passengers = passengers
		self.world = world
		self.tree = Tree()

	def mean(self, cluster):
		x = 0
		y = 0
		for el in cluster:
			x += el["startCoords"][0] + el["endCoords"][0]
			y += el["startCoords"][1] + el["endCoords"][1]
		return (int(x/(len(cluster) * 2), int(y/(len(cluster) * 2))))

	def euclid(self, p1, p2):
		return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

	def cluster(self, clusters):
		byMeans = list()
		for cluster in clusters:
			dat = cluster.data
			byMeans.append(self.mean(dat))

		clustered = list()

		while(len(byMeans) != 0):
			tree = Tree()
			tree.left = clusters.pop()
			mean = byMeans.pop()

			minDist = sys.maxInt()
			minInd = 0

			for i in range(len(byMeans)):
				dist = self.euclid(mean, byMeans[i])

				if(dist < minDist):
					minDist = dist
					minInd = i

			del byMeans[minInd]
			tree.right = cluster[minInd]
			del cluster[minInd]

			tree.data = tree.right.data.extend(tree.left.data)

			clustered.append(tree)
		return clustered


	def agglomerative(self, roots):
		treeLst = list()
		for root in roots:
			treeList.append(Tree(root))

		while(len(TreeList) > 1):
			treeLIst = self.cluster(treeList)

		return treeList

