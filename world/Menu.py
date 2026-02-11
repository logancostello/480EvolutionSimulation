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
            self._stats_lines = [
                self.font.render(f"Creatures: {num_creatures}", True, (255, 255, 255)),
                self.font.render(f"Food: {num_food}", True, (255, 255, 255)),
            ]
            self._last_stats = stats_key
        
        # text_surface = self._stats_cache
        # rect = text_surface.get_rect()
        # pygame.draw.rect(text_surface, (255, 255, 255), rect, 1)
        x, y = 10, 10
        for i, surf in enumerate(self._stats_lines):
            screen.blit(surf, (x, y + i * self.font.get_linesize()))

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

        sorted_creatures = sorted(self.creatures, key=lambda c: c.energy, reverse=True)

        # Update or create buttons
        for i, creature in enumerate(sorted_creatures):
            if cur_y + BUTTON_HEIGHT > self.menu_height:
                break  # Stop if we exceed menu height

            if self.buttons[i] is None or self.buttons[i].creature != creature:
                self.buttons[i] = CreatureButton(creature, pygame.Rect(10, cur_y, self.menu_width - 20, BUTTON_HEIGHT))
            else:
                # Update rect position if creature is the same
                self.buttons[i].rect.y = cur_y
            cur_y += BUTTON_HEIGHT
        
        for b in self.buttons:
            if b is not None:
                b.draw(screen, cursor, selected=False)

    def get_clicked_button(self, pos):
        for b in self.buttons:
            if b is not None and b.hit(pos):
                return b
        return None

class CreatureButton:
    def __init__(self, creature, rect):
        self.creature = creature
        self.rect = rect
        self.font = get_menu_font()  # Reuse cached font

        self._id_surf = self.font.render("", True, (240, 240, 245))
        self._energy_surf = self.font.render("", True, (240, 240, 245))

        # Cache for rendered text
        self._text_cache = {}
        self._last_energy = None

    def label(self):
        return f"Creature:{self.creature.id} \nEnergy: {self.creature.getEnergy():.1f}\n"
    
    def draw(self, surf, mouse_pos, selected=False):
        hover = self.rect.collidepoint(mouse_pos)
        bg = (70, 70, 85) if hover else (55, 55, 65)
        if selected:
            bg = (85, 75, 55)

        pygame.draw.rect(surf, bg, self.rect, border_radius=10)
        pygame.draw.rect(surf, (110, 110, 130), self.rect, 2, border_radius=10)

        energy_rounded = round(self.creature.getEnergy(), 1)

        # (1) Re-render only if changed
        if energy_rounded != self._last_energy:
            self._id_surf = self.font.render(f"Creature:{self.creature.id}", True, (240, 240, 245))
            self._energy_surf = self.font.render(f"Energy: {energy_rounded:.1f}", True, (240, 240, 245))
            self._last_energy = energy_rounded

        # (2) BUT blit every frame
        y = self.rect.y + 12
        surf.blit(self._id_surf, (self.rect.x + 10, y))
        y += self.font.get_linesize()
        surf.blit(self._energy_surf, (self.rect.x + 10, y))
            
        

    def hit(self, pos):
        return self.rect.collidepoint(pos)