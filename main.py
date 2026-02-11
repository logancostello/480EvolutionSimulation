import pygame
import sys
from Simulation import Simulation
from Camera import Camera

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

SIMULATION_WIDTH = 12000
SIMULATION_HEIGHT = 8000

BLACK = (0, 0, 0)

simulation = Simulation(SIMULATION_WIDTH, SIMULATION_HEIGHT)
simulation.initialize()

# Create screen
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Evolution Simulation")

camera = Camera(SIMULATION_WIDTH, SIMULATION_HEIGHT)  

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

        camera.handle_event(event)
    
    screen.fill(BLACK)

    simulation.update(dt)

    simulation.draw(screen, camera)

    pygame.display.flip()    

pygame.quit()
sys.exit()
