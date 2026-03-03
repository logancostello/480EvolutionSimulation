import pygame
import sys
import random
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

FIXED_DT = 1.0 / 60.0  # Simulation always ticks at 60fps equivalent

if len(sys.argv) == 2:
    seed = int(sys.argv[1])
else:
    seed = random.randint(0, 2**32 - 1)

print(f"Simulating with seed = {seed}")
random.seed(seed)

# Create screen
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Evolution Simulation")

datastore = SimulationDatastore()
simulation = Simulation(SIMULATION_WIDTH, SIMULATION_HEIGHT, datastore)
simulation.initialize()
menu = Menu(MENU_WIDTH, MENU_HEIGHT)
menu.draw(screen)  # Initial draw to set up menu surface

camera = Camera(SIMULATION_WIDTH, SIMULATION_HEIGHT)

# Clock for controlling framerate
clock = pygame.time.Clock()
TARGET_FPS = 60

# Speed uncapping toggle
uncapped_mode = False
paused = False
show_menu = True
max_steps_per_frame = 100

# Accumulator for normal (real-time) mode
accumulator = 0.0

# Auto-adjustment for uncapped mode
steps_per_frame = 1
frames_since_adjustment = 0
adjustment_interval = 30
MIN_FPS = 25

# Main update loop
running = True
while running:

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key == pygame.K_m:
                show_menu = not show_menu
            if event.key == pygame.K_a:
                uncapped_mode = not uncapped_mode
                steps_per_frame = 1
                accumulator = 0.0  # Reset accumulator when toggling
                print(f"Uncapped mode: {'ON' if uncapped_mode else 'OFF'}")
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                clicked_button = menu.get_clicked_button(event.pos)
                if clicked_button is not None:
                    camera.center_creature(clicked_button.creature)
                    print(f"Button clicked for Creature ID: {clicked_button.creature.id}")
        camera.handle_event(event)

    screen.fill(BLACK)

    if paused:
        clock.tick(TARGET_FPS)

    else:
        real_dt = clock.tick(TARGET_FPS) / 1000.0

        if uncapped_mode:
            # Run a fixed number of ticks per frame as fast as possible.
            # FIXED_DT is always used — deterministic tick-for-tick given the same seed.
            for _ in range(steps_per_frame):
                simulation.update(FIXED_DT)

            # Auto-adjust how many ticks we squeeze per frame based on performance
            frames_since_adjustment += 1
            if frames_since_adjustment >= adjustment_interval:
                frames_since_adjustment = 0
                actual_fps = clock.get_fps()

                if actual_fps > 50 and steps_per_frame < max_steps_per_frame:
                    steps_per_frame += 1
                elif actual_fps < MIN_FPS and steps_per_frame > 1:
                    steps_per_frame = max(1, steps_per_frame - 1)

        else:
            # Normal mode: tick the simulation to keep pace with real time,
            # but always advance by FIXED_DT so behaviour is identical to uncapped mode
            # tick-for-tick. At 60fps real time this runs exactly 1 tick per frame.
            accumulator += real_dt
            steps = 0
            while accumulator >= FIXED_DT and steps < max_steps_per_frame:
                simulation.update(FIXED_DT)
                accumulator -= FIXED_DT
                steps += 1

        if show_menu:
            menu.update_stats(simulation)

    simulation.draw(screen, camera)
    if show_menu:
        menu.draw(screen)

    pygame.display.flip()

pygame.quit()
datastore.close()
sys.exit()