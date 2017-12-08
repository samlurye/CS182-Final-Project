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

#classes controlling multiagent interatction
class MultiAgent:

	def __init__(self, cars, passengers, world):
		self.cars = cars
		self.customerData = passengers
		self.passengers = passengers.waitingCustomers
		self.world = world
		self.prm = self.world.prm

	#euclidean distance between two points
	def euclid(self, start, end):
		return math.sqrt((start[0] - end[0])**2 + (start[1] - end[1])**2)

	# compares the distance of two points to the position of the car
	def compPoints(self, x, y, car):
		distx = self.euclid(x, car.xy)
		disty = self.euclid(y, car.xy)
		if distx < disty:
			return -1
		elif distx > disty:
			return 1
		else:
			return 0

	# naively picks up all passengers before dropping them off
	def naiveGetPaths(self, travelPoints):
		plan = dict()
		for car in self.cars:
			startpoints = list()
			endpoints = list()
			points = list()
			for point in travelPoints[car.IDnumber]:
				startpoints.append(point["startCoords"])
				endpoints.append(point["endCoords"])
			points.extend(startpoints.sort(lambda x, y: dist(x, y ,start)))
			points.extend(endpoints.sort(lambda x, y: dist(x, y ,start)))
			path = list()
			path.append(self.prm.getPaths(car.xy, points[0], self.world))
			for i in range(len(points) - 1):
				path.append(self.prm.getPaths(points[i], points[i + 1], self.world))
			plan[car.IDnumber] = path
		return plan

	# inserts points into a list based on relative distance to the car
	def orderedInsert(self, lst, el, car):
		for i in range(len(lst)):
			if(self.compPoints(el, lst[i], car) == -1):
				return lst.insert(i, el)
		return lst.append(el)

	# orders points for car to travel to greedily, based on shortest distance
	# to next point
	def greedyGetPaths(self, travelPoints, maxPassengers = 4):
		plans = dict()
		for car in self.cars:
			xy = car.xy
			orderedpts = list()
			path = list()
			front = []
			stateDict = dict()
			for pt in self.passengers:
				front.insert(0, pt["startCoords"])
				stateDict[pt["startCoords"]] = pt["endCoords"]

			while len(front) != 0:
				mindist = sys.maxint
				minpt = None
				for pt in front:
					if self.euclid(pt, xy) < mindist:
						mindist = self.euclid(pt, xy)
						minpt = pt
				if minpt in stateDict:
					front.insert(0, stateDict[minpt])
				front.remove(minpt)
				xy = minpt
				orderedpts.append(minpt)

			plans[car.IDnumber] = orderedpts
		return plans
			
# assigns passengers to cars using k-means clustering
class KMeansClusteringAgent(MultiAgent):

	def __init__(self, cars, passengers, world):
		MultiAgent.__init__(self, cars, passengers, world)
		self.means = dict()
		self.clusters = dict()
		
	# assigns starting means based on positions of cars in world
	def getStartingMeans(self):
		for car in self.cars:
			self.means[car.IDnumber] = car.xy

	#distance function for sorting passengers - returns of the sum of the euclidean distances
	# of the start and endpoints to the car
	def dist(self, mean, passenger):
		return self.euclid(mean, passenger["startCoords"]) + self.euclid(mean, passenger["endCoords"])

	# assigns passengers to a mean for the first time
	def assignMeans(self):
		for mean in self.means.keys():
			self.clusters[mean] = []
		for passenger in self.passengers:
			minDist = sys.maxint
			minMean = 0
			for mean in self.means.keys():
				dist = self.dist(self.means[mean], passenger)
				if(dist < minDist):
					minDist = dist
					minMean = mean
			self.clusters[minMean].append(passenger)

	# updates the position of the means based on the averrage point in the cluster
	def updateMeans(self):
		for mean in self.means.keys():
			x = 0
			y = 0
			if(len(self.clusters[mean]) > 0):
				for p in self.clusters[mean]:
					x += p["startCoords"][0] + p["endCoords"][0]
					y += p["startCoords"][1] + p["endCoords"][1]
				self.means[mean] = (int(x / (len(self.clusters[mean] * 2))), \
									int(y / (len(self.clusters[mean] * 2))))

	# changes assignments of points in the cluster
	def updateClusters(self):
		swap = False
		updates = dict()
		for cluster in self.clusters.keys():
			for passenger in self.clusters[cluster]:
				minDist = sys.maxint
				minMean = cluster
				for mean in self.means.keys():
					dist = self.dist(self.means[mean], passenger)
					if(dist < minDist):
						minDist = dist
						minMean = mean
				if minMean != cluster:
					swap = True
					if not minMean in updates:
						updates[minMean] = []
					updates[minMean].append(passenger)
					self.clusters[cluster].remove(passenger)
		for el in updates.keys():
			self.clusters[el].extend(updates[el])
		return swap

	#runs k-means
	def KMeans(self):
		self.getStartingMeans()
		self.assignMeans()

		while True:
			self.updateMeans()

			if not self.updateClusters():
				break
		print self.clusters
		return self.clusters

	#gets paths based on cluster assignments
	def getPaths(self):
		return MultiAgent.greedyGetPaths(self, self.clusters)

# tree for agglomerative clustering
class Tree:
	def __init__(self, data = None, left = None, right = None):
		self.left = left
		self.right = right
		self.data = data

#agent that clusters points based on the agglomerative clustering algorithm 
# (NOT used)
class AgglomerativeAgent:
	def __init__(self, cars, passengers, world):
		self.means = dict()

		self.clusters = dict()
		self.cars = cars
		self.passengers = passengers
		self.world = world
		self.tree = Tree()
		self.paths = dict()

	# takes the mean of a cluster
	def mean(self, cluster):
		x = 0
		y = 0
		for el in cluster:
			x += el["startCoords"][0] + el["endCoords"][0]
			y += el["startCoords"][1] + el["endCoords"][1]
		return (int(x/(len(cluster) * 2), int(y/(len(cluster) * 2))))

	# takes the euclidean distance between two points
	def euclid(self, p1, p2):
		return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

	# clusters close trees together based on distance between averages of
	# clusters
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

	# gets clusters a given depth in a tree
	def getClusters(tree, num):
		if(len(tree) > num):
			return tree
		
		newtree = list()
		for t in tree:
			newtree.append(t.left)
			newtree.append(t.right)
		return getClusters(newtree, num)

	# runs agglomerative clustering
	def agglomerative(self, roots):
		treeLst = list()
		for root in roots:
			treeList.append(Tree(root))

		while(len(TreeList) > 1):
			treeList = self.cluster(treeList)

		return treeList

	# gets the paths assigned to cars based on their clusters
	def getPaths(self):
		trees = self.getClusters(self.tree, len(self.cars))
		clusters = dict()
		for i in len(trees):
			clusters[i] = tree[i].data
		return MultiAgent.getPaths(self, clusters)

#assigns passengers to cars at random
class RandomMultiAgent(MultiAgent):

	def __init__(self, cars, passengers, world):
		MultiAgent.__init__(self, cars, passengers, world)
		self.clusters = dict()

	def getClusters(self):
		for car in self.cars:
			self.clusters[car.IDnumber] = []
		for passenger in self.passengers:
			car = numpy.random.randint(0, len(self.cars))
			self.clusters[self.cars[car].IDnumber].append(passenger)

	def getPaths(self):
		paths = dict()
		for car in self.cars:
			points = list()
			cluster = self.clusters[car.IDnumber]
			front = list()
			endpts = dict()
			for c in cluster:
				front.append(c["startCoords"])
				endpts[c["startCoords"]] = c["endCoords"]
			while len(front) > 0:
				pt = front.pop(numpy.random.randint(0, len(front)))
				if pt in endpts:
					front.append(endpts[pt])
					del endpts[pt]
				points.append(pt)
			paths[car.IDnumber] = points
		return paths
