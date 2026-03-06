import pygame
from config import ENERGY_DENSITY

class Food:
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius
        self.color = (92, 169, 4)  # Green
        self.energy = ENERGY_DENSITY * self.radius ** 2

        self.sprites = []

        self.sprites.append(pygame.image.load("Assets/Images/apple.png").convert_alpha())

        self.image = self.sprites[0].subsurface(self.sprites[0].get_bounding_rect())

        self.image = pygame.transform.scale(self.image, (radius * 2, radius * 2))

  

    def draw(self, screen, camera):
        screen_pos = camera.world_to_screen((self.pos.x, self.pos.y))

        self.image_scaled = pygame.transform.scale_by(self.image, camera.zoom)
        screen.blit(self.image_scaled, (screen_pos[0], screen_pos[1]))
