import pygame
import math
import random

from entities.Brain import Brain
from entities.Genome import Genome
from spacial.Point import Point

REPRODUCTION_CHANCE = 0.025  # per frame

BASAL_METABOLIC_RATE_ENERGY_PENALTY = 0.3
MOVEMENT_ENERGY_PENALTY = 0.6
SENSORY_ENERGY_PENALTY = 0.2
NUM_BRAIN_NODES_ENERGY_PENALTY = 0.04
NUM_BRAIN_CONNECTION_ENERGY_PENALTY = 0.01

MIN_DESIRE_FOR_REPRODUCTION = 0.01 # [-1, 1]

DEFAULT_MAX_ENERGY = 60

class Creature:
    def __init__(self, id, pos, genome, parent=None, generation=1):
        self.id = id
        self.genome = genome
        self.parent = parent  # the id of the parent creature
        self.generation = generation  # number of generations this lineage has
        self.age = 0
        self.pos = pos
        self.direction = 6.28 * random.random()
        self.energy = genome.init_energy
        self.lifetime_energy_spent = 0
        self.time_since_reproduced = 0
        self.brain = Brain(n_inputs=4, n_outputs=3)

        # Brain outputs
        self.turn_rate = 0
        self.speed = 0
        self.desire_to_reproduce = 0

    @property
    def mass(self):
        return (self.genome.radius / Genome.gene_metadata["radius"]["default"]) ** 2

    @property
    def max_energy(self):
        """ Max energy scales with creature mass """
        return DEFAULT_MAX_ENERGY * self.mass
    
    @property
    def num_brain_nodes(self):
        return len(self.brain.nodes)
    
    @property
    def num_brain_connections(self):
        return len(self.brain.connections.keys())

    def update(self, dt, food_list):
        """
        Make all updates to self each frame
        """

        closest_food_distance, closest_food_direction = self.find_food(food_list)

        # Outputs between [-1, 1]
        brain_outputs = self.brain.think([
            1,  # constant input
            closest_food_direction,
            closest_food_distance,
            self.energy
        ])

        self.turn_rate = self.genome.max_turn_rate * brain_outputs[0]  # [-max_turn_rate, max_turn_rate]
        self.speed = ((brain_outputs[1] + 1) / 2) * self.genome.max_speed  # [0, max_speed]
        self.desire_to_reproduce = brain_outputs[2] # [-1, 1]

        if self.age > 2 or self.parent is None:
            # Rotate direction
            self.direction += self.turn_rate * dt

            # Move
            self.pos.x += math.cos(self.direction) * self.speed * dt
            self.pos.y += math.sin(self.direction) * self.speed * dt

        # Energy and time updates
        energy_cost = self.calculate_energy_loss() * dt
        self.energy -= energy_cost
        self.lifetime_energy_spent += energy_cost
        self.time_since_reproduced += dt
        self.age += dt

    def distance_to_food(self, food):
        """ Returns the distance of food object from creature """
        return math.hypot((food.pos.x - self.pos.x), (food.pos.y - self.pos.y))

    def direction_to_food(self, food):
        """ Return the relative direction of food object to creature """
        diff_x = food.pos.x - self.pos.x
        diff_y = food.pos.y - self.pos.y
        angle_to_point = math.atan2(diff_y, diff_x)
        delta = angle_to_point - self.direction
        normalised_delta = (delta + math.pi) % (2 * math.pi) - math.pi
        return normalised_delta

    def find_food(self, nearby_food):
        """ Returns the distance and direction to the single closest food item, if one is in vision"""
        # defaults if none visible
        dist_to_closest = self.genome.viewable_distance
        dir_to_closest = 0

        # check if each food is in FOV and closest
        for food_piece in nearby_food:
            dist = self.distance_to_food(food_piece)
            dir = self.direction_to_food(food_piece)

            if abs(dir) <= self.genome.fov and dist < dist_to_closest:
                dist_to_closest = dist
                dir_to_closest = dir

        # normalize
        dist_to_closest /= self.genome.viewable_distance

        return dist_to_closest, dir_to_closest

    def can_reproduce(self):
        """ Returns a boolean indicating if the creature can spawn a child """

        # Check enough time has passed
        if self.time_since_reproduced < self.genome.time_between_reproduction:
            return False

        # Check enough energy to reproduce
        if self.energy < self.genome.energy_for_reproduction:
            return False

        # Check wants to reproduce
        if self.desire_to_reproduce < MIN_DESIRE_FOR_REPRODUCTION:
            return False

        return True
    
    def reproduce(self, child_id):
        """ Returns a child creature """
        # Reset time since reproduced
        self.time_since_reproduced = 0

        # Get child creature
        child_pos = Point(self.pos.x, self.pos.y)
        child = Creature(child_id, child_pos, self.genome.clone(), self.id, self.generation + 1)
        child.speed = self.speed
        child.direction = self.direction
        child.brain = self.brain.clone()

        # Apply mutations
        child.brain.mutate()
        child.genome.mutate()

        # Adjust energy
        energy_for_child = self.energy * self.genome.percent_energy_for_child
        child.energy = energy_for_child
        self.energy -= energy_for_child

        return child
    
    def calculate_energy_loss(self):
        """ 
        Returns energy loss per second 
        Default creature loses ~1 energy per second
        """
        mass = self.mass

        basal = BASAL_METABOLIC_RATE_ENERGY_PENALTY * mass

        movement = MOVEMENT_ENERGY_PENALTY * mass * (self.speed / self.genome.max_speed) ** 2

        sensory = SENSORY_ENERGY_PENALTY * (self.genome.fov / Genome.gene_metadata["fov"]["default"]) * (self.genome.viewable_distance / Genome.gene_metadata["viewable_distance"]["default"])

        neural = NUM_BRAIN_NODES_ENERGY_PENALTY * self.num_brain_nodes + NUM_BRAIN_CONNECTION_ENERGY_PENALTY * self.num_brain_connections

        return basal + movement + sensory + neural

    def draw(self, screen, camera):
        screen_pos = camera.world_to_screen((self.pos.x, self.pos.y))
        scaled_radius = self.genome.radius * camera.zoom
        color = (int(self.genome.color_r), int(self.genome.color_g), int(self.genome.color_b))
        pygame.draw.circle(screen, color, (int(screen_pos[0]), int(screen_pos[1])), int(scaled_radius))

    def getEnergy(self):
        return self.energy
