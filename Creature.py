import pygame
import math
import random

from Brain import Brain

MAX_SPEED = 100 # 100 pixels per second
MAX_TURN_RATE = math.pi # 180 degrees per second

DEFAULT_DIRECTION = 0
DEFAULT_RADIUS = 25
DEFAULT_COLOR = (255, 255, 255) # white
DEFAULT_ENERGY = 30
DEFAULT_MIN_TIME_BETWEEN_REPRODUCING = 20
DEFAULT_MIN_ENERGY_TO_REPRODUCE = 15

REPRODUCTION_CHANCE = 0.1 # per frame

class Creature(pygame.sprite.Sprite):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = DEFAULT_DIRECTION  # angle in radians
        self.radius = DEFAULT_RADIUS # pixels
        self.color = DEFAULT_COLOR
        self.energy = DEFAULT_ENERGY # number of seconds it can survive
        self.min_energy_to_reproduce = DEFAULT_MIN_ENERGY_TO_REPRODUCE
        self.time_since_reproduced = 0
        self.min_time_between_reproducing = DEFAULT_MIN_TIME_BETWEEN_REPRODUCING
        self.brain = Brain(n_inputs=3, n_outputs=2)

        # Brain outputs
        self.turn_rate = 0.5 
        self.speed = 50

        # Adding Sprite Animation
        self.sprites = []
        self.sprites.append(pygame.image.load("Assets/Images/Moving_Frame_1.png"))
        self.sprites.append(pygame.image.load("Assets/Images/Moving_frame_2.png"))

        self.current_sprite = 0

        self.image = self.sprites[self.current_sprite]
        self.image_original = self.sprites[self.current_sprite]
        

        self.rect = self.image.get_rect(center = (x, y))

        #self.rect.topleft = [x,y]

    def is_alive(self):
        return self.energy > 0
    
    def update(self, dt):
        """
        Make all updates to self each frame
        """
        #if self.current_sprite == 0:
            #self.current_sprite = 1
        #else: 
            #self.current_sprite = 0
    
        if not self.is_alive(): return

        # Outputs between [-1, 1]
        brain_outputs = self.brain.think([
            1, # constant input
            self.energy,
            self.direction,
        ])
       
        self.turn_rate = MAX_TURN_RATE * brain_outputs[0] # [-max_turn_rate, max_turn_rate]
        self.speed = ((brain_outputs[1] + 1) / 2) * MAX_SPEED # [0, max_speed]

        # Rotate direction
        self.direction += self.turn_rate * dt
       

        initial_center = self.image.get_rect(center = (self.x, self.y))
        self.image = pygame.transform.rotate(self.image_original, self.direction)

        

        # Move
        self.x += math.cos(self.direction) * self.speed * dt
        self.y += math.sin(self.direction) * self.speed * dt

        # Use energy
        self.energy -= dt
        self.time_since_reproduced += dt

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
        #self.image = pygame.transform.scale(self.image_original, scaled_radius)
        screen.blit(self.image, (int(screen_pos[0]), int(screen_pos[1]) ))
        pygame.draw.circle(screen, self.color, (int(screen_pos[0]), int(screen_pos[1])), int(scaled_radius))
        
     