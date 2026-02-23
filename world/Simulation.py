import random
import pygame

from entities.Creature import Creature
from entities.Genome import Genome
from spacial.Point import Point
from spacial.QuadTree import QuadTree
from world.FoodSpawner import FoodSpawner

NUM_INIT_CREATURE = 300
NUM_INIT_FOOD = 1000

CONTACT_DAMAGE = 10

class Simulation:
    def __init__(self, world_width, world_height, datastore):
        self.simulation_width = world_width
        self.simulation_height = world_height
        self.datastore = datastore
        self.time = 0  # in seconds
        self.creatures = []
        self.food = QuadTree(Point(0, 0), Point(world_width, world_height), 10, 10)
        self.creature_tree = QuadTree(Point(0, 0), Point(world_width, world_height), 10, 10)
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
            self.creature_tree.insert(creature)
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

        orig_num_creatures = len(self.creatures)
        orig_num_food = len(self.food.get_all())

        for c in self.creatures:
            nearby_food = self.food.get_nearby(c.pos, c.genome.viewable_distance)
            c.update(dt, nearby_food)

        self.handle_eating()

        self.handle_contact()

        self.handle_creature_death()

        self.handle_reproduction()

        if len(self.creatures) != orig_num_creatures or len(self.food.get_all()) != orig_num_food:
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

    def handle_contact(self):
        # check for collisions between creatures and transfer energy
        for c in self.creatures:
            for other in self.creatures:
                if c.id != other.id:
                    dist = (c.pos.x - other.pos.x) ** 2 + (c.pos.y - other.pos.y) ** 2
                    collision_distance = (c.genome.radius + other.genome.radius) ** 2

                    if dist < collision_distance:
                        # simple energy transfer: each creature gives the other 10% of their energy
                        c.energy -= CONTACT_DAMAGE - (CONTACT_DAMAGE * (c.genome.radius / other.genome.radius))
                        other.energy -= CONTACT_DAMAGE - (CONTACT_DAMAGE * (other.genome.radius / c.genome.radius))

    def handle_reproduction(self):
        new_creatures = []
        for c in self.creatures:
            if c.can_reproduce():
                child = c.reproduce(self.next_creature_id)
                self.next_creature_id += 1
                new_creatures.append(child)
                self.datastore.add_new_creature(child, self.time)
                self.creature_tree.insert(child)  # Add child to creature tree immediately
        self.creatures += new_creatures

    def handle_creature_death(self):
        dead = [c for c in self.creatures if c.energy <= 0]
        for creature in dead:
            self.energy_pool += creature.lifetime_energy_spent
            self.datastore.mark_creature_dead(creature.id, self.time)
            self.creature_tree.remove(creature)  # Remove dead creature from creature tree
        self.creatures = [c for c in self.creatures if c.energy > 0]

    def food_list(self):
        return self.food