import math
import random
import pygame

from Creature import Creature
from Food import Food

SYS_FONT = None
BUTTON_HEIGHT = 60

class Menu:
    def __init__(self, menu_width, menu_height):
        self.menu_width = menu_width
        self.menu_height = menu_height

        self.font = pygame.font.SysFont(SYS_FONT, 24)
        self.creatures = []
        self.creatures_a = []
        self.num_creatures_a = 0
        self.num_creatures_d = 0
        self.num_food = 0

        self.buttons = []

    def update_stats(self, simulation):
        self.creatures_a = [c for c in simulation.creatures if c.is_alive()]
        self.num_creatures_a = len([c for c in simulation.creatures if c.is_alive()])
        self.num_creatures_d = len([c for c in simulation.creatures if not c.is_alive()])
        self.num_food = len(simulation.food)

    def display_stats(self, screen):
        num_creatures_a = self.num_creatures_a
        num_creatures_d = self.num_creatures_d
        num_food = self.num_food

        stats_text = f"Creatures Alive: {num_creatures_a}\nCreatures Dead: {num_creatures_d}\nFood: {num_food}"
        text_surface = self.font.render(stats_text, True, (255, 255, 255))
        rect = text_surface.get_rect()
        # rect = pygame.Rect(10, 10, self.menu_width-10, BUTTON_HEIGHT, width=5)
        pygame.draw.rect(text_surface, (255, 255, 255), rect, 1)
        screen.blit(text_surface, (10, 10))

    def draw(self, screen):
        # Draw menu background
        pygame.draw.rect(screen, (110, 110, 130), (0, 0, self.menu_width, self.menu_height), width=5)

        self.display_stats(screen)
        self.update_buttons(screen)

    def update_buttons(self, screen):
        self.buttons = []
        cur_y = BUTTON_HEIGHT + 10

        cursor = pygame.mouse.get_pos()

        # For creature in the number of creatures, we should draw stats for each creature
        for creature in self.creatures_a:
            self.buttons.append(CreatureButton(creature, pygame.Rect(10, cur_y, self.menu_width - 20, BUTTON_HEIGHT)))
            cur_y += BUTTON_HEIGHT
        
        for b in self.buttons:
            b.draw(screen, cursor, selected=(False))

class CreatureButton:
    def __init__(self, creature, rect):
        self.creature = creature
        self.rect = rect
        self.font = pygame.font.SysFont(SYS_FONT, 24)

    def label(self):
        return f"Creature: \nEnergy: {self.creature.getEnergy():.1f}\n"
    
    
    def draw(self, surf, mouse_pos, selected=False):
        hover = self.rect.collidepoint(mouse_pos)
        bg = (70, 70, 85) if hover else (55, 55, 65)
        if selected:
            bg = (85, 75, 55)

        pygame.draw.rect(surf, bg, self.rect, border_radius=10)
        pygame.draw.rect(surf, (110, 110, 130), self.rect, 2, border_radius=10)

        txt = self.font.render(self.label(), True, (240, 240, 245))
        surf.blit(txt, (self.rect.x + 10, self.rect.y + 12))

    def hit(self, pos):
        return self.rect.collidepoint(pos)
    