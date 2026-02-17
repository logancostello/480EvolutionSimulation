import random
import pygame

from entities.Creature import Creature
from entities.Food import Food
from entities.Genome import Genome
from spacial.Point import Point
from spacial.QuadTree import QuadTree
from entities.Forest import Forest

NUM_INIT_CREATURE = 75
NUM_INIT_FOOD = 1000
NUM_TARGET_FOOD = NUM_INIT_FOOD
NUM_INIT_FORESTS = 5

MAX_FOOD_RADIUS = 10


class Simulation:
    def __init__(self, world_width, world_height, datastore):
        self.simulation_width = world_width
        self.simulation_height = world_height
        self.datastore = datastore
        self.time = 0  # in seconds
        self.creatures = []
        self.food = QuadTree(Point(0, 0), Point(world_width, world_height), 10, 10)
        self.next_creature_id = 1
        self.forest = []
        self.total_forest_weights = 2  # starting number is the likelihood of food appearing outside a forest

    def initialize(self):
        # randomly generate creatures throughout world
        for _ in range(NUM_INIT_CREATURE):
            pos = self.spawn_random_point()
            default_genome = Genome.create_default()
            creature = Creature(self.next_creature_id, pos, default_genome)

            # give random colors to make lineages visible
            creature.genome.color_r = random.randint(Genome.gene_metadata["color_r"]["min"], Genome.gene_metadata["color_r"]["max"])
            creature.genome.color_g = random.randint(Genome.gene_metadata["color_g"]["min"], Genome.gene_metadata["color_r"]["max"])
            creature.genome.color_b = random.randint(Genome.gene_metadata["color_b"]["min"], Genome.gene_metadata["color_r"]["max"])

            self.creatures.append(creature)
            self.datastore.add_new_creature(creature, self.time)
            self.next_creature_id += 1

        # randomly generate forests throughout the world
        for forest in range(NUM_INIT_FORESTS):
            pt = self.spawn_random_point()
            wt = random.randint(1, 3)
            r_x = random.randint(500, 1500)
            r_y = random.randint(500, 1500)
            self.forest.append(Forest(pt, wt, r_x, r_y))
            self.total_forest_weights += wt

        # randomly generate food within forests
        for forest in self.forest:
            food_count = round(NUM_INIT_FOOD * (forest.weight/self.total_forest_weights))

            for food in range(food_count):
                pos = self.spawn_point_in_forest(forest)
                self.food.insert(Food(pos, MAX_FOOD_RADIUS))

        # randomly generate additional food throughout world
        leftover_food = NUM_INIT_FOOD - len(self.food.get_all())
        for _ in range(leftover_food):
            pos = self.spawn_random_point()
            self.food.insert(Food(pos, MAX_FOOD_RADIUS))

        self.datastore.update_real_time(self.time, len(self.creatures), len(self.food.get_all()))

    def spawn_random_point(self):
        x = self.simulation_width * random.random()
        y = self.simulation_height * random.random()
        return Point(x, y)

    def spawn_point_in_forest(self, forest):
        x = forest.position.x + random.randint(-forest.radius_x, forest.radius_x)
        y = forest.position.y + random.randint(-forest.radius_y, forest.radius_y)

        if 0 < x < self.simulation_width and 0 < y < self.simulation_height:  # if within world boundary

            # normalised distance from forest center
            nx = (x - forest.position.x) / forest.radius_x
            ny = (y - forest.position.y) / forest.radius_y
            norm = nx * nx + ny * ny

            if norm > 1.0:  # if outside of ellipsis
                return self.spawn_point_in_forest(forest)

            if (norm ** 0.5) <= 0.75:  # accept all points in inner 75% of forest
                return Point(x, y)
            elif random.randint(0, 2) == 0:  # 1/3 as likely in outer 25% of forest
                return Point(x, y)

        return self.spawn_point_in_forest(forest)

    def update(self, dt):
        self.time += dt

        orig_num_creatures = len(self.creatures)
        orig_num_food = len(self.food.get_all())

        for c in self.creatures:
            nearby_food = self.food.get_nearby(c.pos, c.genome.viewable_distance)
            c.update(dt, nearby_food)

        self.handle_eating()

        self.handle_creature_death()

        self.handle_reproduction()

        if len(self.creatures) != orig_num_creatures or len(self.food.get_all()) != orig_num_food:
            self.datastore.update_real_time(self.time, len(self.creatures), len(self.food.get_all()))

        self.handle_food_spawning()

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
            for f in self.food.get_nearby(c.pos, c.genome.radius + MAX_FOOD_RADIUS):
                dist = (c.pos.x - f.pos.x) ** 2 + (c.pos.y - f.pos.y) ** 2
                collision_distance = (c.genome.radius + f.radius) ** 2

                # if colliding, the creature gets the food's energy
                if dist < collision_distance:
                    c.energy += f.energy
                    c.energy = min(c.max_energy, c.energy)
                    f.energy = 0 # set to zero incase another creature is also touching food
                    eaten.add(f)

        # remove eaten food from memory
        for e in eaten:
            self.food.remove(e)

    def handle_reproduction(self):
        new_creatures = []
        for c in self.creatures:
            if c.can_reproduce():
                child = c.reproduce(self.next_creature_id)
                self.next_creature_id += 1
                new_creatures.append(child)
                self.datastore.add_new_creature(child, self.time)
        self.creatures += new_creatures

    def handle_creature_death(self):
        dead = [c for c in self.creatures if c.energy <= 0]
        for creature in dead:
            self.datastore.mark_creature_dead(creature.id, self.time)
        self.creatures = [c for c in self.creatures if c.energy > 0]

    def food_list(self):
        return self.food

    def handle_food_spawning(self):
        food_alive = 0
        for f in self.food.get_all():
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
                    self.food.insert(Food(pt, MAX_FOOD_RADIUS))
                    return

            pt = self.spawn_random_point()
            self.food.insert(Food(pt, MAX_FOOD_RADIUS))
            return
