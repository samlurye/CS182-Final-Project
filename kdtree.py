import time
import random
import math
from scipy.spatial import cKDTree

class KDTree:

	def __init__(self, dim, points, axis=0):
		self.dim = dim
		self.axis = axis
		points = sorted(points, key=lambda p: p[axis])
		self.numPoints = len(points)
		medianIndex = self.numPoints / 2
		self.value = points[medianIndex]
		self.left = None
		self.right = None
		leftPoints = points[:medianIndex]
		rightPoints = points[medianIndex+1:]
		if leftPoints != []:
			self.left = KDTree(self.dim, leftPoints, (axis + 1) % self.dim)
		if rightPoints != []:
			self.right = KDTree(self.dim, rightPoints, (axis + 1) % self.dim)

	def insert(self, point):
		assert len(point) == self.dim
		if point == self.value:
			return
		elif point[self.axis] >= self.value[self.axis]:
			if self.right:
				self.right.insert(point)
			else:
				self.right = KDTree(self.dim, [point], (self.axis + 1) % self.dim)
				return
		elif self.left:
			self.left.insert(point)
		else:
			self.left = KDTree(self.dim, [point], (self.axis + 1) % self.dim)
			return

	def contains(self, point, depth=0):
		assert len(point) == self.dim
		if point == self.value:
			return True
		elif point[self.axis] >= self.value[self.axis]:
			if self.right:
				return self.right.contains(point, depth + 1)
			else:
				return False
		elif self.left:
			return self.left.contains(point, depth + 1)
		else:
			return False

	def kInsert(self, point, d, kBest, k):
		if len(kBest) < k:
			kBest.append((point, d))
		else:
			maxD = -float("inf")
			maxI = 0
			for i in range(len(kBest)):
				if kBest[i][1] > maxD:
					maxD = kBest[i][1]
					maxI = i
			if d < maxD:
				kBest[maxI] = (point, d)

	def kNearestNeighbors(self, point, k, kBest):
		if not self.left and not self.right:
			self.kInsert(self.value, self.squareDist(point, self.value), kBest, k)
			return kBest
		searchedRight = False
		if point[self.axis] > self.value[self.axis]:
			searchedRight = True
			if self.right:
				self.right.kNearestNeighbors(point, k, kBest)
		elif self.left:
			self.left.kNearestNeighbors(point, k, kBest)
		self.kInsert(self.value, self.squareDist(point, self.value), kBest, k)
		maxK = max(kBest, key=lambda x: x[1])
		if searchedRight and maxK[1] > abs(point[self.axis] - self.value[self.axis]) ** 2:
			if self.left:
				self.left.kNearestNeighbors(point, k, kBest)
		elif not searchedRight and maxK[1] > abs(point[self.axis] - self.value[self.axis]) ** 2:
			if self.right:
				self.right.kNearestNeighbors(point, k, kBest)		
		return kBest

	def squareDist(self, p1, p2):
		sd = 0
		for i in range(self.dim):
			sd += (p1[i] - p2[i]) ** 2
		return sd

