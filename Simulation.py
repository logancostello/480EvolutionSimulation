import math
import random

from Creature import Creature
from Food import Food

NUM_INIT_FOOD = 50

class Simulation:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.creatures = []
        self.food = []

        self.food.append(Food(self.screen_width * 2 // 3, self.screen_height // 2))

    def initialize(self):
        # hard code add one creature for now
        self.creatures.append(Creature(self.screen_width // 2, self.screen_height // 2))

        # randomly generate food throughout world
        for _ in range(NUM_INIT_FOOD):
            self.spawn_random_food()

    def spawn_random_food(self):
        x = self.screen_width * random.random()
        y = self.screen_height * random.random()
        f = Food(x, y)
        self.food.append(f)

    def update(self, dt):
        for c in self.creatures:
            c.update(dt)

        self.handle_eating()

        self.handle_reproduction()        

    def draw(self, screen):
        for f in self.food:
            f.draw(screen)
    
        for c in self.creatures:
            c.draw(screen)

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