import math
import random
import pygame

from Creature import Creature
from Food import Food
from Forest import Forest

NUM_INIT_CREATURE = 3
NUM_INIT_FOOD = 1000
NUM_TARGET_FOOD = NUM_INIT_FOOD
NUM_INIT_FORESTS = 5


class Simulation:
    def __init__(self, world_width, world_height):
        self.simulation_width = world_width
        self.simulation_height = world_height

        self.creatures = []
        self.food = []
        self.forest = []
        self.total_forest_weights = 2 # starting number is the likelihood of food appearing outside a forest

    def initialize(self):
        # randomly generate creatures throughout world
        for c in range(NUM_INIT_CREATURE):
            pt = self.spawn_random_point()
            self.creatures.append(Creature(pt[0], pt[1]))

        # randomly generate forests throughout the world
        for forest in range(NUM_INIT_FORESTS):
            pt = self.spawn_random_point()
            wt = random.randint(1, 3)
            r_x = random.randint(500, 1500)
            r_y = random.randint(500, 1500)
            self.forest.append(Forest(pt[0], pt[1], wt, r_x, r_y))
            self.total_forest_weights += wt

        # randomly generate food within forests
        for forest in self.forest:
            food_count = round(NUM_INIT_FOOD * (forest.weight/self.total_forest_weights))

            for food in range(food_count):
                pt = self.spawn_point_in_forest(forest)
                self.food.append(Food(pt[0], pt[1]))

        # randomly generate additional food throughout world
        leftover_food = NUM_INIT_FOOD - len(self.food)
        for food in range(leftover_food):
            pt = self.spawn_random_point()
            self.food.append(Food(pt[0], pt[1]))

    def spawn_random_point(self):
        x = self.simulation_width * random.random()
        y = self.simulation_height * random.random()
        return x, y

    def spawn_point_in_forest(self, forest):
        x = forest.x + random.randint(-forest.radius_x, forest.radius_x)
        y = forest.y + random.randint(-forest.radius_y, forest.radius_y)

        if 0 < x < self.simulation_width and 0 < y < self.simulation_height:  # if within world boundary

            # normalised distance from forest center
            nx = (x - forest.x) / forest.radius_x
            ny = (y - forest.y) / forest.radius_y
            norm = nx * nx + ny * ny

            if norm > 1.0:  # if outside of ellipsis
                return self.spawn_point_in_forest(forest)

            if (norm ** 0.5) <= 0.75:  # accept all points in inner 75% of forest
                return x, y
            elif random.randint(0, 2) == 0:  # 1/3 as likely in outer 25% of forest
                return x, y

        return self.spawn_point_in_forest(forest)

    def update(self, dt):
        for c in self.creatures:
            c.update(dt, self.food_list())

        self.handle_eating()

        self.handle_reproduction()

        self.handle_food_spawning()

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

    def handle_food_spawning(self):
        food_alive = 0
        for f in self.food:
            if f.is_alive():
                food_alive += 1

        food_to_spawn = NUM_TARGET_FOOD - food_alive

        for food in range(food_to_spawn):
            r = random.random()

            cumulative = 0

            for forest in self.forest:
                cumulative += forest.weight/self.total_forest_weights
                if r < cumulative:
                    pt = self.spawn_point_in_forest(forest)
                    self.food.append(Food(pt[0], pt[1]))
                    return

            pt = self.spawn_random_point()
            self.food.append(Food(pt[0], pt[1]))
            return
