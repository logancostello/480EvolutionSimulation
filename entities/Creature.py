import pygame
import math
import random

from entities.Brain import Brain
from spacial.Point import Point

MAX_SPEED = 100  # 100 pixels per second
MAX_TURN_RATE = math.pi  # 180 degrees per second

DEFAULT_DIRECTION = 0
DEFAULT_RADIUS = 25
DEFAULT_COLOR = (255, 255, 255)  # white
DEFAULT_ENERGY = 30
DEFAULT_MIN_TIME_BETWEEN_REPRODUCING = 20
DEFAULT_MIN_ENERGY_TO_REPRODUCE = 15
VIEWABLE_DISTANCE = 150  # number of pixels the creature can see in front of themselves
VIEWABLE_ANGLE = math.pi / 2

REPRODUCTION_CHANCE = 0.1  # per frame


class Creature:
    def __init__(self, id, pos, parent=None, generation=1):
        self.id = id
        self.parent = parent # the id of the parent creature
        self.generation = generation # number of generations this lineage has
        self.age = 0
        self.pos = pos
        self.direction = DEFAULT_DIRECTION  # angle in radians
        self.max_speed = MAX_SPEED
        self.max_turn_rate = MAX_TURN_RATE
        self.radius = DEFAULT_RADIUS  # pixels
        self.color = DEFAULT_COLOR
        self.energy = DEFAULT_ENERGY  # number of seconds it can survive
        self.min_energy_to_reproduce = DEFAULT_MIN_ENERGY_TO_REPRODUCE
        self.time_since_reproduced = 0
        self.min_time_between_reproducing = DEFAULT_MIN_TIME_BETWEEN_REPRODUCING
        self.brain = Brain(n_inputs=3, n_outputs=2)
        self.viewable_distance = VIEWABLE_DISTANCE
        self.viewable_angle = VIEWABLE_ANGLE

        # Brain outputs
        self.turn_rate = 0.5
        self.speed = 50

    def update(self, dt, food_list):
        """
        Make all updates to self each frame
        """

        closest_food_distance, closest_food_direction = self.find_food(food_list)

        # Outputs between [-1, 1]
        brain_outputs = self.brain.think([
            1,  # constant input
            closest_food_direction,
            closest_food_distance
        ])

        self.turn_rate = self.max_turn_rate * brain_outputs[0]  # [-max_turn_rate, max_turn_rate]
        self.speed = ((brain_outputs[1] + 1) / 2) * self.max_speed  # [0, max_speed]

        if self.age > 2 or self.parent is None:
            # Rotate direction
            self.direction += self.turn_rate * dt

            # Move
            self.pos.x += math.cos(self.direction) * self.speed * dt
            self.pos.y += math.sin(self.direction) * self.speed * dt

        # Energy and time updates
        self.energy -= dt
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
        dist_to_closest = self.viewable_distance
        dir_to_closest = 0

        # check if each food is in FOV and closest
        for food_piece in nearby_food:
            dist = self.distance_to_food(food_piece)
            dir = self.direction_to_food(food_piece)

            if abs(dir) <= self.viewable_angle and dist < dist_to_closest:
                dist_to_closest = dist
                dir_to_closest = dir

        # normalize
        dist_to_closest /= self.viewable_distance

        return dist_to_closest, dir_to_closest

    def can_reproduce(self):
        """ Returns a boolean indicating if the creature can spawn a child """

        # Check enough time has passed
        if self.time_since_reproduced < self.min_time_between_reproducing:
            return False

        # Check enough energy to reproduce
        if self.energy < self.min_energy_to_reproduce:
            return False

        # All conditions met, random chance to reproduce
        if random.random() > REPRODUCTION_CHANCE:
            return False

        return True
    
    def reproduce(self, child_id):
        """ Returns a child creature """
        # Reset time since reproduced
        self.time_since_reproduced = 0

        # Get child creature
        child_pos = Point(self.pos.x, self.pos.y)
        child = Creature(child_id, child_pos, self.id, self.generation + 1)
        child.speed = self.speed
        child.direction = self.direction
        child.brain = self.brain.clone()

        # Apply mutations
        child.mutate()

        return child

    def mutate(self):
        """" Applies random mutations to creature """
        self.brain.mutate()

    def draw(self, screen, camera):
        screen_pos = camera.world_to_screen((self.pos.x, self.pos.y))
        scaled_radius = self.radius * camera.zoom
        pygame.draw.circle(screen, self.color, (int(screen_pos[0]), int(screen_pos[1])), int(scaled_radius))

    def getEnergy(self):
        return self.energy
