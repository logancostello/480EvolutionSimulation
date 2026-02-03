import pygame
import math
import random

from Brain import Brain

MAX_SPEED = 100  # 100 pixels per second
MAX_TURN_RATE = math.pi  # 180 degrees per second

DEFAULT_DIRECTION = 0
DEFAULT_RADIUS = 25
DEFAULT_COLOR = (255, 255, 255)  # white
DEFAULT_ENERGY = 30
DEFAULT_MIN_TIME_BETWEEN_REPRODUCING = 20
DEFAULT_MIN_ENERGY_TO_REPRODUCE = 15
VIEWABLE_DISTANCE = 20  # number of pixels the creature can see in front of themselves

REPRODUCTION_CHANCE = 0.1  # per frame


class Creature:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = DEFAULT_DIRECTION  # angle in radians
        self.radius = DEFAULT_RADIUS  # pixels
        self.color = DEFAULT_COLOR
        self.energy = DEFAULT_ENERGY  # number of seconds it can survive
        self.min_energy_to_reproduce = DEFAULT_MIN_ENERGY_TO_REPRODUCE
        self.time_since_reproduced = 0
        self.min_time_between_reproducing = DEFAULT_MIN_TIME_BETWEEN_REPRODUCING
        self.brain = Brain(n_inputs=5, n_outputs=2)

        # Brain outputs
        self.turn_rate = 0.5
        self.speed = 50

    def is_alive(self):
        return self.energy > 0

    def update(self, dt, food_list):
        """
        Make all updates to self each frame
        """
        if not self.is_alive(): return

        closest_food_direction, closest_food_distance = self.find_food(food_list)

        # Outputs between [-1, 1]
        brain_outputs = self.brain.think([
            1,  # constant input
            self.energy,
            self.direction,
            closest_food_direction,
            closest_food_distance
        ])

        self.turn_rate = MAX_TURN_RATE * brain_outputs[0]  # [-max_turn_rate, max_turn_rate]
        self.speed = ((brain_outputs[1] + 1) / 2) * MAX_SPEED  # [0, max_speed]

        # Rotate direction
        self.direction += self.turn_rate * dt

        # Move
        self.x += math.cos(self.direction) * self.speed * dt
        self.y += math.sin(self.direction) * self.speed * dt

        # Use energy
        self.energy -= dt
        self.time_since_reproduced += dt

    def distance_to_food(self, food):
        """ Returns the distance of food object from creature, if food is within VIEWABLE_DISTANCE """
        dist = math.hypot((food.x - self.x), (food.y - self.y))
        if VIEWABLE_DISTANCE >= dist:
            return dist
        return None

    def direction_to_food(self, food):
        """ Returns the amount to turn to face the food, if food is within .5 radians of direction. """
        diff_x = food.x - self.x
        diff_y = food.y - self.y

        angle_to_point = math.atan2(diff_y, diff_x)
        delta = angle_to_point - self.direction
        normalised_delta = (delta + math.pi) % (2 * math.pi) - math.pi
        if abs(normalised_delta) <= 0.25:
            return normalised_delta

        return None

    def find_food(self, food_list):
        """ Returns the distance and direction to the single closest food item, if one is in vision"""
        dist = float('inf')
        turn = float('inf')

        for food_piece in food_list:
            if self.distance_to_food(food_piece) is not None and self.direction_to_food(food_piece) is not None:
                if self.distance_to_food(food_piece) < dist:
                    dist = self.distance_to_food(food_piece)
                    turn = self.direction_to_food(food_piece)

        return dist, turn

    def can_reproduce(self):
        """ Returns a boolean indicating if the creature can spawn a child """
        if not self.is_alive():
            return False

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

    def clone(self):
        """ Returns a new creature with the same genes as parent """
        # Reset time since reproduced
        self.time_since_reproduced = 0

        # Deep copy
        new_creature = Creature(self.x, self.y)
        new_creature.speed = self.speed
        new_creature.direction = self.direction
        new_creature.brain = self.brain.clone()
        return new_creature

    def mutate(self):
        """" Applies random mutations to creature """
        self.brain.mutate()

    def draw(self, screen, camera):
        if not self.is_alive():
            return

        screen_pos = camera.world_to_screen((self.x, self.y))
        scaled_radius = self.radius * camera.zoom
        pygame.draw.circle(screen, self.color, (int(screen_pos[0]), int(screen_pos[1])), int(scaled_radius))
