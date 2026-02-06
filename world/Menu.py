import math
import random
import pygame

from entities.Creature import Creature
from entities.Food import Food

SYS_FONT = None
BUTTON_HEIGHT = 60

# Create font once at module level
_MENU_FONT = None

def get_menu_font():
    global _MENU_FONT
    if _MENU_FONT is None:
        _MENU_FONT = pygame.font.SysFont(SYS_FONT, 24)
    return _MENU_FONT

class Menu:
    def __init__(self, menu_width, menu_height):
        self.menu_width = menu_width
        self.menu_height = menu_height

        self.font = get_menu_font()  # Reuse cached font
        self.creatures = []
        self.num_food = 0

        self.buttons = []
        
        # Cache for rendered stats text
        self._stats_cache = {}
        self._last_stats = None

    def update_stats(self, simulation):
        self.creatures = simulation.creatures
        self.num_food = len(simulation.food.get_all())

    def display_stats(self, screen):
        num_creatures = len(self.creatures)
        num_food = self.num_food

        # Cache key
        stats_key = (num_creatures, num_food)
        
        # Only re-render if stats changed
        if stats_key != self._last_stats:
            stats_text = f"Creatures: {num_creatures}\nFood: {num_food}"
            self._stats_cache = self.font.render(stats_text, True, (255, 255, 255))
            self._last_stats = stats_key
        
        text_surface = self._stats_cache
        rect = text_surface.get_rect()
        pygame.draw.rect(text_surface, (255, 255, 255), rect, 1)
        screen.blit(text_surface, (10, 10))

    def draw(self, screen):
        # Draw menu background
        pygame.draw.rect(screen, (110, 110, 130), (0, 0, self.menu_width, self.menu_height), width=5)

        self.display_stats(screen)
        self.update_buttons(screen)

    def update_buttons(self, screen):
        # Reuse existing buttons instead of recreating
        cur_y = BUTTON_HEIGHT + 10
        cursor = pygame.mouse.get_pos()

        # Resize button list if needed
        while len(self.buttons) < len(self.creatures):
            self.buttons.append(None)
        while len(self.buttons) > len(self.creatures):
            self.buttons.pop()

        # Update or create buttons
        for i, creature in enumerate(self.creatures):
            if self.buttons[i] is None or self.buttons[i].creature != creature:
                self.buttons[i] = CreatureButton(creature, pygame.Rect(10, cur_y, self.menu_width - 20, BUTTON_HEIGHT))
            else:
                # Update rect position if creature is the same
                self.buttons[i].rect.y = cur_y
            cur_y += BUTTON_HEIGHT
        
        for b in self.buttons:
            b.draw(screen, cursor, selected=False)

class CreatureButton:
    def __init__(self, creature, rect):
        self.creature = creature
        self.rect = rect
        self.font = get_menu_font()  # Reuse cached font
        
        # Cache for rendered text
        self._text_cache = {}
        self._last_energy = None

    def label(self):
        return f"Creature: \nEnergy: {self.creature.getEnergy():.1f}\n"
    
    def draw(self, surf, mouse_pos, selected=False):
        hover = self.rect.collidepoint(mouse_pos)
        bg = (70, 70, 85) if hover else (55, 55, 65)
        if selected:
            bg = (85, 75, 55)

        pygame.draw.rect(surf, bg, self.rect, border_radius=10)
        pygame.draw.rect(surf, (110, 110, 130), self.rect, 2, border_radius=10)

        # Cache rendered text based on energy value
        energy = self.creature.getEnergy()
        energy_rounded = round(energy, 1)  # Round to avoid cache misses from float precision
        
        if energy_rounded != self._last_energy:
            label_text = self.label()
            self._text_cache = self.font.render(label_text, True, (240, 240, 245))
            self._last_energy = energy_rounded
        
        surf.blit(self._text_cache, (self.rect.x + 10, self.rect.y + 12))

    def hit(self, pos):
        return self.rect.collidepoint(pos)