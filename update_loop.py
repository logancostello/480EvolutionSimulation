import pygame
import sys
from Simulation import Simulation

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

BLACK = (0, 0, 0)

simulation = Simulation(SCREEN_WIDTH, SCREEN_HEIGHT)
simulation.initialize()

# Create screen
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Evolution Simulation")

# Clock for controlling framerate
clock = pygame.time.Clock()
FPS = 60

# Main update loop
running = True
while running:

    dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(BLACK)

    simulation.update(dt)

    simulation.draw(screen)

    pygame.display.flip()    

pygame.quit()
sys.exit()