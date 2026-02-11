import pygame
import sys
from world.Simulation import Simulation
from world.Menu import Menu
from world.Camera import Camera
from telemetry.SimulationDatastore import SimulationDatastore

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

datastore = SimulationDatastore()
simulation = Simulation(SIMULATION_WIDTH, SIMULATION_HEIGHT, datastore)
simulation.initialize()
menu = Menu(MENU_WIDTH, MENU_HEIGHT)
menu.draw(screen)

camera = Camera(SIMULATION_WIDTH, SIMULATION_HEIGHT)  

# Clock for controlling framerate
clock = pygame.time.Clock()
FPS = 60

# Speed uncapping toggle
uncapped_mode = False
paused = False
show_menu = True
TARGET_FPS = 60
MIN_FPS = 25
FIXED_DT = 1.0 / 60.0
simulation_steps_per_frame = 1
max_steps_per_frame = 100
frames_since_adjustment = 0
adjustment_interval = 30

# Main update loop
running = True
while running:

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            datastore.close()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_m:
                show_menu = not show_menu
            if event.key == pygame.K_a:
                uncapped_mode = not uncapped_mode
                simulation_steps_per_frame = 1  # Reset when toggling
                print(f"Uncapped mode: {'ON' if uncapped_mode else 'OFF'}")

        camera.handle_event(event)
    
    screen.fill(BLACK)

    if paused:
        clock.tick()

    else:
        if uncapped_mode:
            # Uncapped mode: run as fast as possible
            real_dt = clock.tick(TARGET_FPS) / 1000.0
            sim_time_advanced = FIXED_DT * simulation_steps_per_frame

            if sim_time_advanced < real_dt:
                simulation.update(real_dt) 
            else:
                for _ in range(simulation_steps_per_frame):
                    simulation.update(FIXED_DT)
            
            # Auto-adjust simulation speed based on performance
            frames_since_adjustment += 1
            if frames_since_adjustment >= adjustment_interval:
                frames_since_adjustment = 0
                actual_fps = clock.get_fps()
                
                if actual_fps > 50 and simulation_steps_per_frame < max_steps_per_frame:
                    simulation_steps_per_frame += 1
                elif actual_fps < MIN_FPS and simulation_steps_per_frame > 1:
                    simulation_steps_per_frame = max(1, simulation_steps_per_frame - 1)
        else:
            # Normal mode: run in real time
            dt = clock.tick(FPS) / 1000.0
            simulation.update(dt)

        if show_menu:
            menu.update_stats(simulation)

    simulation.draw(screen, camera)
    if show_menu:
        menu.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
