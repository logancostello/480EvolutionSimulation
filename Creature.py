import pygame
import math
import random

from Brain import Brain

MAX_ACCELERATION = 5
MAX_TURN_RATE = 5

class Creature:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = 0  # angle in radians
        self.speed = 10  # pixels per second
        self.radius = 10
        self.color = (255, 255, 255)  # White
        self.energy = 30 # number of seconds it can survive
        self.brain = Brain(n_inputs=6, n_outputs=2)

        # Brain outputs
        self.turn_rate = 0 
        self.acceleration = 0

    def is_alive(self):
        return self.energy > 0
    
    def update(self, dt):
        """
        Make all updates to self each frame
        """
        if not self.is_alive(): return

        brain_outputs = self.brain.think([
            1, # constant input
            self.energy,
            self.acceleration,
            self.turn_rate,
            self.speed,
            self.direction
        ])

        self.turn_rate = MAX_TURN_RATE * brain_outputs[0]
        self.acceleration = MAX_ACCELERATION * brain_outputs[1]

        # Rotate direction
        self.direction += self.turn_rate * dt
        self.speed += self.acceleration * dt

        # Move in direction
        self.x += math.cos(self.direction) * self.speed * dt
        self.y += math.sin(self.direction) * self.speed * dt

        # Use energy
        self.energy -= dt

    def can_reproduce(self):
        """
        Returns a boolean indicating if the creature can spawn a child
        """
        return self.is_alive() and random.random() < 0.001 # 0.1% chance per frame
    
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
        if self.is_alive():
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)