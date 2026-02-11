import pygame


class Forest:
    def __init__(self, x, y, weight, radius_x, radius_y):
        self.x = x
        self.y = y
        self.weight = weight
        self.radius_x = radius_x
        self.radius_y = radius_y
        self.color = (self.chooseColor())

    def chooseColor(self):
        if self.weight == 1:
            return 106, 161, 74  # light forest green
        if self.weight == 2:
            return 77, 120, 52  # medium forest green
        if self.weight == 3:
            return 60, 95, 47  # dark forest green

    def draw(self, screen, camera):  # will add background color to world later
        pass
