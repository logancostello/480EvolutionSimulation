import pygame
import math
import random

from entities.Brain import Brain
from entities.Genome import Genome
from spacial.Point import Point

from config import DEFAULT_MAX_ENERGY, BASAL_METABOLIC_RATE_ENERGY_PENALTY, MOVEMENT_ENERGY_PENALTY, SENSORY_ENERGY_PENALTY, NUM_BRAIN_CONNECTION_ENERGY_PENALTY, NUM_BRAIN_NODES_ENERGY_PENALTY

class Creature:
    _sprites = None

    @classmethod
    def _load_sprites(cls):
        if cls._sprites is None:
            cls._sprites = [
                pygame.image.load("Assets/Images/Moving_Frame_1.png").convert_alpha(),
                pygame.image.load("Assets/Images/Moving_frame_2.png").convert_alpha(),
            ]

    def __init__(self, id, pos, genome, parent=None, generation=1):
        Creature._load_sprites()

        self.update_count = 0
        self.id = id
        self.genome = genome
        self.parent = parent
        self.generation = generation
        self.age = 0
        self.pos = pos
        self.direction = 6.28 * random.random()
        self.energy = genome.init_energy
        self.lifetime_energy_spent = 0
        self.time_since_reproduced = 0
        self.brain = Brain.create_basic_brain(n_inputs=8, n_outputs=3, num_mutations=1)

        self.turn_rate = 0
        self.speed = 0
        self.desire_to_reproduce = 0

        self.sprites = Creature._sprites
        self.current_sprite = 0

        image = self.sprites[0].subsurface(self.sprites[0].get_bounding_rect())
        width, height = image.get_size()
        size = max(width, height)
        square_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        square_surface.blit(image, ((size - width) // 2, (size - height) // 2))

        self.image_original = square_surface
        self.image_copy = self.image_original.copy()
        self.rect = self.image_original.get_rect(center=(self.pos.x, self.pos.y))

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

    def update(self, dt, nearby_food, nearby_creatures):
        """Make all updates to self each frame"""

        closest_food_dis, closest_food_dir, count_food_in_vision = self.find_food(nearby_food)
        closest_creature_dis, closest_creature_dir, count_creatures_in_vision = self.find_creature(nearby_creatures)

        # Outputs between [-1, 1]
        brain_outputs = self.brain.think([
            1,  # constant input
            closest_food_dir,
            closest_food_dis,
            count_food_in_vision,
            closest_creature_dir,
            closest_creature_dis,
            count_creatures_in_vision,
            self.energy
        ])

        self.turn_rate = self.genome.max_turn_rate * brain_outputs[0]  # [-max_turn_rate, max_turn_rate]
        self.speed = ((brain_outputs[1] + 1) / 2) * self.genome.max_speed  # [0, max_speed]
        self.desire_to_reproduce = brain_outputs[2]  # [-1, 1]

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
        """ Returns the distance of food object from creature. """
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
        """ Returns the normalized distance(0 to 1) and direction to the single closest food item, if one is in vision,
            and returns the total count of food items in vision."""
        # defaults if none visible
        dist_to_closest = self.genome.viewable_distance
        dir_to_closest = 0
        count_in_vision = 0

        # check if each food is in FOV and closest
        for food_piece in nearby_food:
            dist = self.distance_to_food(food_piece)
            dir = self.direction_to_food(food_piece)

            if abs(dir) <= self.genome.fov:
                count_in_vision += 1
                if dist < dist_to_closest:
                    dist_to_closest = dist
                    dir_to_closest = dir

        # normalize
        dist_to_closest /= self.genome.viewable_distance

        return dist_to_closest, dir_to_closest, count_in_vision

    def distance_to_creature(self, creature):
        """ Returns the distance of food object from creature. """
        return math.hypot((creature.pos.x - self.pos.x), (creature.pos.y - self.pos.y))

    def direction_to_creature(self, diff_x, diff_y):
        """ Return the relative direction of food object to creature """
        angle_to_point = math.atan2(diff_y, diff_x)
        delta = angle_to_point - self.direction
        normalised_delta = (delta + math.pi) % (2 * math.pi) - math.pi
        return normalised_delta

    def find_creature(self, nearby_creatures):
        """ Returns the normalized distance(0 to 1) and direction to the single closest creature, if one is in vision,
            and returns the total count of creatures in vision."""
        # defaults if none visible
        dist_sq = self.genome.viewable_distance * self.genome.viewable_distance
        dist_to_closest = dist_sq
        dir_to_closest = 0
        count_in_vision = 0

        # check if each food is in FOV and closest
        for creature_object in nearby_creatures:
            # skip self
            if creature_object.id == self.id:
                continue

            # early reject
            diff_x = creature_object.pos.x - self.pos.x
            diff_y = creature_object.pos.y - self.pos.y
            dist = diff_x * diff_x + diff_y * diff_y
            if dist > dist_sq:
                continue

            # exact reject
            dir = self.direction_to_creature(diff_x, diff_y)

            if abs(dir) <= self.genome.fov:
                count_in_vision += 1
                if dist < dist_to_closest:
                    dist_to_closest = dist
                    dir_to_closest = dir

        # normalize
        dist_to_closest /= self.genome.viewable_distance

        return dist_to_closest, dir_to_closest, count_in_vision

    def can_reproduce(self):
        """ Returns a boolean indicating if the creature can spawn a child """

        # Check enough time has passed
        if self.time_since_reproduced < self.genome.time_between_reproduction:
            return False

        # Check enough energy to reproduce
        if self.energy < self.genome.energy_for_reproduction:
            return False

        # Check wants to reproduce
        if self.desire_to_reproduce < 0.01:
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
    
    def change_sprite_frame(self):
        """
        Changes the sprite frame 
        """

        if self.update_count == 7:

            self.update_count = 0

            if self.current_sprite == 0:
                self.current_sprite = 1

            else:
                self.current_sprite = 0

            # Original Image

            image = self.sprites[self.current_sprite].subsurface(self.sprites[self.current_sprite].get_bounding_rect())
            width, height = image.get_size()
            size = max(width, height)
            square_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            square_surface.blit(image, ((size- width) //2, (size - height) //2))

            # Maintain original image

            self.image_original = square_surface
        
            # Make a copy of the image for modification

            self.image_copy = self.image_original.copy()

        self.update_count = self.update_count + 1


    def draw(self, screen, camera):

        self.change_sprite_frame()

        screen_pos = camera.world_to_screen((self.pos.x, self.pos.y))

        scaled_radius = self.genome.radius * camera.zoom

        # Change the Image Color

        color = (int(self.genome.color_r), int(self.genome.color_g), int(self.genome.color_b))

        pixel_array = pygame.PixelArray(self.image_copy)

        pixel_array.replace((217, 30, 217), color)

        pixel_array.replace((217, 35, 150), color)

        del pixel_array

        # Scale the image

        diameter = int(self.genome.radius * 2)

        image_scaled =  pygame.transform.smoothscale(self.image_copy, (diameter, diameter))

        # Rotate and Zoom the image

        image_rotated_zoom = pygame.transform.rotozoom(image_scaled, -math.degrees(self.direction) + 90 + 180, camera.zoom)

        scaled_rect = image_rotated_zoom.get_rect(center=screen_pos)

        screen.blit(image_rotated_zoom, scaled_rect)

    def getEnergy(self):
        return self.energy
