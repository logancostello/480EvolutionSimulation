import random
import pygame

from entities.Creature import Creature
from entities.Food import Food

NUM_INIT_CREATURE = 50
NUM_INIT_FOOD = 1000


class Simulation:
    def __init__(self, world_width, world_height):
        self.simulation_width = world_width
        self.simulation_height = world_height

        self.creatures = []
        self.food = []

    def initialize(self):
        # randomly generate creatures throughout world
        for _ in range(NUM_INIT_CREATURE):
            x, y = self.spawn_random_point()
            self.creatures.append(Creature(x, y))

        # randomly generate food throughout world
        for _ in range(NUM_INIT_FOOD):
            x, y = self.spawn_random_point()
            self.food.append(Food(x, y))

    def spawn_random_point(self):
        x = self.simulation_width * random.random()
        y = self.simulation_height * random.random()
        return x, y

    def update(self, dt):
        for c in self.creatures:
            c.update(dt, self.food)

        self.handle_eating()

        self.handle_creature_death()

        self.handle_reproduction()

    def draw(self, screen, camera):
        visible_area = camera.get_visible_area()
        visible_rect = pygame.Rect(visible_area)

        for f in self.food:
            if visible_rect.collidepoint(f.x, f.y):
                f.draw(screen, camera)

        for c in self.creatures:
            if visible_rect.collidepoint(c.x, c.y):
                c.draw(screen, camera)

    def handle_eating(self):

        # check for collisions between creatures and food
        eaten = set()
        for c in self.creatures:
            for f in self.food:
                dist = (c.x - f.x) ** 2 + (c.y - f.y) ** 2
                collision_distance = (c.radius + f.radius) ** 2

                # if colliding, the creature gets the food's energy
                if dist < collision_distance:
                    c.energy += f.energy
                    f.energy = 0 # set to zero incase another creature is also touching food
                    eaten.add(f)

        # remove eaten food from memory
        self.food = [f for f in self.food if f not in eaten]

    def handle_reproduction(self):
        new_creatures = []
        for c in self.creatures:
            if c.can_reproduce():
                child = c.clone()
                child.mutate()
                new_creatures.append(child)
        self.creatures += new_creatures

    def handle_creature_death(self):
        self.creatures = [c for c in self.creatures if c.energy > 0]