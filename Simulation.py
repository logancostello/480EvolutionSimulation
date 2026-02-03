import math
import random
import pygame

from Creature import Creature
from Food import Food

NUM_INIT_CREATURE = 3
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
            pt = self.spawn_random_point()
            self.creatures.append(Creature(pt[0], pt[1]))

        # randomly generate food throughout world
        for _ in range(NUM_INIT_FOOD):
            pt = self.spawn_random_point()
            self.food.append(Food(pt[0], pt[1]))

    def spawn_random_point(self):
        x = self.simulation_width * random.random()
        y = self.simulation_height * random.random()
        return x, y

    def update(self, dt):
        for c in self.creatures:
            c.update(dt, self.food_list())

        self.handle_eating()

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
        for c in self.creatures:
            if not c.is_alive():
                continue

            for f in self.food:
                if not f.is_alive():
                    continue

                dist = math.sqrt((c.x - f.x) ** 2 + (c.y - f.y) ** 2)
                collision_distance = c.radius + f.radius

                if dist < collision_distance:
                    c.energy += f.energy
                    f.energy = 0

    def handle_reproduction(self):
        new_creatures = []
        for c in self.creatures:
            if c.can_reproduce():
                child = c.clone()
                child.mutate()
                new_creatures.append(child)
        self.creatures += new_creatures

    def food_list(self):
        return self.food
