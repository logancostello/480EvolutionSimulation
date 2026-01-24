import pygame

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.color =  (92,169,4)  # Green
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)