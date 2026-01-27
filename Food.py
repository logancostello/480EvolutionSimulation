import pygame

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.color =  (92,169,4)  # Green
        self.energy = 2 # number of seconds it adds to a creatures life when eaten

    def is_alive(self):
        return self.energy > 0
    
    def draw(self, screen):
        if self.is_alive():
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)