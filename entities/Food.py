import pygame
from config import ENERGY_DENSITY

class Food:
    _sprite = None

    @classmethod
    def _load_sprite(cls, radius):
        if cls._sprite is None:
            raw = pygame.image.load("Assets/Images/apple.png").convert_alpha()
            cropped = raw.subsurface(raw.get_bounding_rect())
            cls._sprite = pygame.transform.scale(cropped, (radius * 2, radius * 2))

    def __init__(self, pos, radius):
        Food._load_sprite(radius)
        self.pos = pos
        self.radius = radius
        self.color = (92, 169, 4)
        self.energy = ENERGY_DENSITY * self.radius ** 2
        self.image = Food._sprite

    def draw(self, screen, camera):
        screen_pos = camera.world_to_screen((self.pos.x, self.pos.y))
        self.image_scaled = pygame.transform.scale_by(self.image, camera.zoom)
        screen.blit(self.image_scaled, (screen_pos[0], screen_pos[1]))