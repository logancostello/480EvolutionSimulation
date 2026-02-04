import random
import pygame

from entities.Creature import Creature
from entities.Food import Food
from spacial.Point import Point
from spacial.QuadTree import QuadTree

NUM_INIT_CREATURE = 50
NUM_INIT_FOOD = 1000


class Simulation:
    def __init__(self, world_width, world_height):
        self.simulation_width = world_width
        self.simulation_height = world_height

        self.creatures = []
        self.food = QuadTree(Point(0, 0), Point(world_width, world_height), 10, 10)

    def initialize(self):
        # randomly generate creatures throughout world
        for _ in range(NUM_INIT_CREATURE):
            pos = self.spawn_random_point()
            self.creatures.append(Creature(pos))

        # randomly generate food throughout world
        for _ in range(NUM_INIT_FOOD):
            pos = self.spawn_random_point()
            self.food.insert(Food(pos))

    def spawn_random_point(self):
        x = self.simulation_width * random.random()
        y = self.simulation_height * random.random()
        return Point(x, y)

    def update(self, dt):
        for c in self.creatures:
            c.update(dt, self.food.get_all())

        self.handle_eating()

        self.handle_creature_death()

        self.handle_reproduction()

    def draw(self, screen, camera):
        visible_area = camera.get_visible_area()
        visible_rect = pygame.Rect(visible_area)

        for f in self.food.get_all():
            if visible_rect.collidepoint(f.pos.x, f.pos.y):
                f.draw(screen, camera)

        for c in self.creatures:
            if visible_rect.collidepoint(c.pos.x, c.pos.y):
                c.draw(screen, camera)

    def handle_eating(self):

        # check for collisions between creatures and food
        eaten = set()
        for c in self.creatures:
            for f in self.food.get_all():
                dist = (c.pos.x - f.pos.x) ** 2 + (c.pos.y - f.pos.y) ** 2
                collision_distance = (c.radius + f.radius) ** 2

                # if colliding, the creature gets the food's energy
                if dist < collision_distance:
                    c.energy += f.energy
                    f.energy = 0 # set to zero incase another creature is also touching food
                    eaten.add(f)

        # remove eaten food from memory
        for e in eaten:
            self.food.remove(e)

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