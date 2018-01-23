import math

class Coordinate:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def sum_y(self, c):
        self.y += c.y

    def average_y(self, factor):
        self.y /= float(factor)

    def findMax(self, c):
        if self.y >= c.y:
            self.y = c.y

    def findMin(self, c):
        if self.y < c.y:
            self.y = c.y

    def get_distance(c1, c2):
        x1 = c1.x
        y1 = c1.y
        x2 = c2.x
        y2 = c2.y
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
