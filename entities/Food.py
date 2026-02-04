import pygame
import math

ENERGY_DENSITY = 0.05

class Food:
    def __init__(self, pos):
        self.pos = pos
        self.radius = 10
        self.color =  (92,169,4)  # Green
        self.energy = ENERGY_DENSITY * math.pi * self.radius ** 2
    
    def draw(self, screen, camera):        
        screen_pos = camera.world_to_screen((self.pos.x, self.pos.y))
        scaled_radius = self.radius * camera.zoom
        pygame.draw.circle(screen, self.color, (int(screen_pos[0]), int(screen_pos[1])), int(scaled_radius))
