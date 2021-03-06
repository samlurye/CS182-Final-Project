from kdtree import KDTree
import random
import time
import math
import heapq

def AStarSearch(edges, start, goal, eps, iterLimit=2500):
    queue = []
    visited = set([start])
    nodesExpanded = 0
    for neighbor in edges[start]:
        cost = dist(neighbor, start)
        heapq.heappush(queue, (cost + dist(neighbor, goal), dict(path = [neighbor], cost = cost)))
    i = 0
    while len(queue) != 0 and i < iterLimit:
        i += 1
        currentInfo = heapq.heappop(queue)[1]
        current = currentInfo["path"][-1]
        if dist(current, goal) <= eps:
            currentInfo["path"][-1] = goal
            return currentInfo["path"]
        if current not in visited:
            nodesExpanded += 1
            visited.add(current)
            cost = currentInfo["cost"]
            successors = edges[current]
            for succ in successors:
                if succ in visited:
                    continue
                else:
                    h = dist(succ, goal)
                    newCost = cost + dist(succ, current)
                    path = currentInfo["path"][:]
                    path.append(succ)
                    heapq.heappush(queue, (newCost + h, dict(path = path, cost = newCost)))
    return []

def dist(p1, p2):
    d = 0
    for i in range(len(p1)):
        d += (p1[i] - p2[i]) ** 2
    return math.sqrt(d)

class RRT:

    """Naive 2-D RRT that doesn't incorporate dynamics into the system"""

    def __init__(self, start, goal):
        self.start = start
        self.goal = goal
        # distance within which tree has 'reached' the goal
        self.eps = 5
        # extension distance
        self.ext = 10
        self.tree = KDTree(len(self.start), [self.start])
        # edges
        self.connections = dict()

    # run the algorithm and return a path from start to goal
    def run(self, world):
        i = 0
        while i < 2500:
            i += 1
            s1 = self.sample(world)
            s = self.tree.kNearestNeighbors(s1, 1, [])[0][0]
            s1e = self.extend(s, s1, world)
            if not s1e:
                continue
            else:
                self.tree.insert(s1e)
                try:
                    self.connections[s].add(s1e)
                except:
                    self.connections[s] = set([s1e])
                try:
                    self.connections[s1e].add(s)
                except:
                    self.connections[s1e] = set([s])
                if dist(s1e, self.goal) < self.eps:
                    return AStarSearch(self.connections, self.start, self.goal, self.eps)
        return []

    # sample world uniformly
    def sample(self, world):
        if random.random() < 0.05:
            return self.goal
        point = (random.random() * world.displayWidth, random.random() * world.displayHeight)
        for obstacle in world.obstacleBeliefs:
            # make sure the point is at least carsize / 2 away from the nearest obstacle
            if obstacle.colliderect((point[0] - world.cars[0].size[0] / 2.,
                point[1] - world.cars[0].size[1] / 2., world.cars[0].size[0], world.cars[0].size[1])):
                return self.sample(world)
        return point

    def extend(self, p1, p2, world):
        pointDir = (p2[0] - p1[0], p2[1] - p1[1])
        magDir = dist(pointDir, (0, 0))
        newPoint = (p1[0] + self.ext * pointDir[0] / magDir, p1[1] + self.ext * pointDir[1] / magDir)
        for obstacle in world.obstacleBeliefs:
            if obstacle.colliderect((newPoint[0] - world.cars[0].size[0] / 2.,
                newPoint[1] - world.cars[0].size[1] / 2., world.cars[0].size[0], world.cars[0].size[1])):
                return None
        return newPoint

class DynamicRRT(RRT):

    """4-dimensional RRT that incorporates physics into the system"""

    def sample(self, world):
        if random.random() < 0.05:
            return self.goal
        point = (
            random.random() * world.displayWidth,
            random.random() * world.displayHeight,
            2 * random.random() * world.cars[0].maxSpeed - world.cars[0].maxSpeed,
            360 * random.random()
        )
        for obstacle in world.obstacleBeliefs:
            if obstacle.collidepoint((point[0], point[1])):
                return self.sample(world)
        return point

    # see report for explanation of this extend operation
    def extend(self, p1, p2, world):
        dirInput = 0
        if p2[2] - p1[2] > 0:
            dirInput = 1
        elif p1[2] - p2[2] > 0:
            dirInput = -1
        rotInput = 0
        bigOrientation = max(p1[3], p2[3])
        smallOrientation = min(p1[3], p2[3])
        fullRotAngle = bigOrientation - smallOrientation
        if fullRotAngle > 180:
            fullRotAngle -= 360
        if fullRotAngle > 0:
            rotInput = world.cars[0].angvel
        else:
            rotInput = -world.cars[0].angvel
        speed = p1[2] - world.cars[0].drag * p1[2] * world.cars[0].dt + dirInput * world.cars[0].acc * world.cars[0].dt
        orientation = p1[3]
        velocity = speed * math.cos(math.radians(orientation)), -speed * math.sin(math.radians(orientation))
        newPoint = (
            p1[0] + velocity[0],
            p1[1] + velocity[1],
            speed,
            (orientation + rotInput) % 360
        )
        for obstacle in world.obstacleBeliefs:
            if obstacle.collidepoint(newPoint):
                return None
        return newPoint


class Paths(dict):

    def __init__(self):
        dict.__init__(self)

    def __getitem__(self, pointPair):
        try:
            return dict.__getitem__(self, pointPair)
        except:
            try:
                return dict.__getitem__(self, (pointPair[1], pointPair[0]))[::-1]
            except:
                raise KeyError

class PRM:

    def __init__(self, world):
        self.points = KDTree(2, [world.kdtreeStart])
        # number of samples in the prm
        self.size = 2500
        # number of connections per sample
        self.connsPerSample = 6
        self.carSize = world.carSize
        self.getPoints(world)
        # edges of the prm
        self.connections = self.getConnections(world)

    # uniformly sample floating point coordinates from the world
    def sample(self, world):
        point = (random.random() * world.displayWidth, random.random() * world.displayHeight)
        for obstacle in world.obstacleBeliefs:
            if obstacle.colliderect((point[0] - self.carSize[0] / 2.,
                point[1] - self.carSize[1] / 2., self.carSize[0], self.carSize[1])):
                return self.sample(world)
        return point

    # uniformly sample integer coordinates from the world
    def sampleInt(self, world):
        point = (random.randint(0, world.displayWidth), random.randint(0, world.displayHeight))
        for obstacle in world.obstacleBeliefs:
            if obstacle.colliderect((point[0] - self.carSize[0] / 2.,
                point[1] - self.carSize[1] / 2., self.carSize[0], self.carSize[1])):
                return self.sampleInt(world)
        return point

    # fill the KD tree
    def getPoints(self, world):
        for _ in range(self.size - 1):
            self.points.insert(self.sample(world))

    # ignore this function
    def getPaths(self, world):
        paths = Paths()
        for p1 in self.connections:
            for p2 in self.connections[p1]:
                print p1, p2
                if p1 == p2:
                    continue
                try:
                    _ = paths[p1, p2]
                except:
                    paths[p1, p2] = RRT(p1, p2).run(world)
        return paths

    # generate a path (a list of points along the prm) from p1 to p2
    def getPath(self, p1, p2, world):
        if not self.points.contains(p1):
            self.insertConnection(p1, world)
        if not self.points.contains(p2):
            self.insertConnection(p2, world)
        path = AStarSearch(self.connections, p1, p2, 5, self.size)
        # use RRT if no path exists along prm
        if not path:
            path = RRT(p1, p2).run(world)
        return path

    # insert a point into the prm
    def insertConnection(self, point, world):
        nns = self.points.kNearestNeighbors(point, self.connsPerSample, [])
        self.connections[point] = []
        for p in nns:
            collided = False
            for obstacle in world.obstacleBeliefs:
                if obstacle.collideline((point[0], point[1], p[0][0], p[0][1]), 10):
                    collided = True
            if not collided:
                self.connections[point].append(p[0])
                self.connections[p[0]].append(point)
        self.points.insert(point)

    # form the prm from the set of sampled points
    def getConnections(self, world):
        connections = dict()
        pointsList = self.points.list()
        for point in pointsList:
            nns = self.points.kNearestNeighbors(point, self.connsPerSample + 1, [])
            connections[point] = []
            for p in nns:
                collided = False
                for obstacle in world.obstacleBeliefs:
                    if obstacle.collideline((point[0], point[1], p[0][0], p[0][1]), 10):
                        collided = True
                if not collided:
                    connections[point].append(p[0])
            connections[point].remove(point)
        return connections








