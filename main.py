import pygame
import sys
from Simulation import Simulation
from Menu import Menu
from Camera import Camera

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

SIMULATION_WIDTH = 12000
SIMULATION_HEIGHT = 8000

MENU_WIDTH = 200
MENU_HEIGHT = SCREEN_HEIGHT

BLACK = (0, 0, 0)

# Create screen
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Evolution Simulation")

simulation = Simulation(SIMULATION_WIDTH, SIMULATION_HEIGHT)
simulation.initialize()
menu = Menu(MENU_WIDTH, MENU_HEIGHT)
menu.draw(screen)

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
    menu.update_stats(simulation)

    simulation.draw(screen, camera)
    # menu.display_stats(screen, camera)
    menu.draw(screen)

    pygame.display.flip()    

pygame.quit()
sys.exit()