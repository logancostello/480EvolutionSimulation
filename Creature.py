import pygame
import math
import random

class Creature:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 0  # angle in radians
        self.speed = 50  # pixels per second
        self.radius = 10
        self.color = (255, 255, 255)  # White
        self.alive = True

        # Brain outputs
        self.turn_rate = 0 
        self.acceleration = 0 # pixels per second^2

    def think(self):
        """
        Compute output nodes of brain, informing the updates to be made
        """
        self.turn_rate = 1.0
        self.acceleration = 5.0
    
    def update(self, dt):
        """
        Make all updates to self each frame
        """
        
        self.think()

        # Rotate direction
        self.direction += self.turn_rate * dt
        self.speed += self.acceleration * dt

        # Move in direction
        self.x += math.cos(self.direction) * self.speed * dt
        self.y += math.sin(self.direction) * self.speed * dt

    def can_reproduce(self):
        """
        Returns a boolean indicating if the creature can spawn a child
        """
        return self.alive and random.random() < 0.001 # 0.1% chance per frame
    
    def clone(self):
        """
        Returns a new creature with the same genes as parent
        """
        return Creature(self.x, self.y)
    
    def mutate(self):
        """"
        Applies random mutations to creature
        """
        self.direction += math.pi # for now just turn the direction around 
        return

    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)