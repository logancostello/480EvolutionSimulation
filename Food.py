import pygame
import math

ENERGY_DENSITY = 0.05

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.color =  (92,169,4)  # Green
        self.energy = ENERGY_DENSITY * math.pi * self.radius ** 2

    def is_alive(self):
        return self.energy > 0
    
    def draw(self, screen, camera):
        if not self.is_alive():
            return
        
        screen_pos = camera.world_to_screen((self.x, self.y))
        scaled_radius = self.radius * camera.zoom
        pygame.draw.circle(screen, self.color, (int(screen_pos[0]), int(screen_pos[1])), int(scaled_radius))
