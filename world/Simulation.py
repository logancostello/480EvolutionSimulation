import random
import pygame

from entities.Creature import Creature
from entities.Genome import Genome
from spacial.Point import Point
from spacial.QuadTree import QuadTree
from world.FoodSpawner import FoodSpawner
from spacial.SpacialHashGrid import SpatialHashGrid

NUM_INIT_CREATURE = 50
NUM_INIT_FOOD = 1000
CELL_SIZE = 100  # determines how large each spacial hash grid cell is


class Simulation:
    def __init__(self, world_width, world_height, datastore):
        self.simulation_width = world_width
        self.simulation_height = world_height
        self.datastore = datastore
        self.time = 0  # in seconds
        self.creatures = []
        self.creature_grid = SpatialHashGrid(CELL_SIZE)
        self.food = QuadTree(Point(0, 0), Point(world_width, world_height), 10, 10)
        self.next_creature_id = 1
        self.food_spawner = FoodSpawner(self, NUM_INIT_FOOD)
        self.energy_pool = 0 

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

        # Initialize forests and food via food spawner
        self.food_spawner.initialize_forests()
        self.food_spawner.initialize_food()

        self.datastore.update_real_time(self.time, len(self.creatures), len(self.food.get_all()))

    def spawn_random_point(self):
        x = self.simulation_width * random.random()
        y = self.simulation_height * random.random()
        return Point(x, y)

    def update(self, dt):
        self.time += dt
        self.creature_grid.clear_frame()

        for c in self.creatures:
            self.creature_grid.insert(c, c.pos.x, c.pos.y)
        for c in self.creatures:
            r = c.genome.viewable_distance
            nearby_food = self.food.get_nearby(c.pos, c.genome.viewable_distance)
            nearby_creatures = self.creature_grid.query_rectangle(c.pos.x - r, c.pos.y - r, c.pos.x + r, c.pos.y + r)
            c.update(dt, nearby_food, nearby_creatures)

        self.handle_eating()

        any_died = self.handle_creature_death()

        any_reproduced = self.handle_reproduction()

        if any_died or any_reproduced:
            self.datastore.update_real_time(self.time, len(self.creatures), len(self.food.get_all()))

        self.food_spawner.spawn_food()

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
            for f in self.food.get_nearby(c.pos, c.genome.radius + 10):  # MAX_FOOD_RADIUS = 10
                dist = (c.pos.x - f.pos.x) ** 2 + (c.pos.y - f.pos.y) ** 2
                collision_distance = (c.genome.radius + f.radius) ** 2

                # if colliding, the creature gets the food's energy
                if dist < collision_distance:
                    max_consumable_energy = c.max_energy - c.energy
                    energy_consumed = min(f.energy, max_consumable_energy)

                    c.energy += energy_consumed
                    f.energy -= energy_consumed
                    eaten.add(f)

        # remove eaten food from memory
        for e in eaten:
            if e.energy <= 0:
                self.food.remove(e)

    def handle_reproduction(self):
        new_creatures = []
        for c in self.creatures:
            if c.can_reproduce():
                child = c.reproduce(self.next_creature_id)
                self.next_creature_id += 1
                new_creatures.append(child)
                self.datastore.add_new_creature(child, self.time)
        self.creatures.extend(new_creatures)
        return bool(new_creatures)  # returns true if creatures reproduced

    def handle_creature_death(self):
        dead = [c for c in self.creatures if c.energy <= 0]
        dead_ids = set(d.id for d in dead)
        for creature in dead:
            self.energy_pool += creature.lifetime_energy_spent
            self.datastore.mark_creature_dead(creature.id, self.time)
            self.creatures = [c for c in self.creatures if c.id not in dead_ids]  # rebuilding is faster then removing
        return bool(dead)  # returns true if creatures died

    def food_list(self):
        return self.food

    def get_creature(self, world_pos):
        tolerance = 50
        for c in self.creatures:
            dist = (c.pos.x - world_pos[0]) ** 2 + (c.pos.y - world_pos[1]) ** 2
            if dist <= c.genome.radius ** 2 + tolerance:
                return c
        return None
