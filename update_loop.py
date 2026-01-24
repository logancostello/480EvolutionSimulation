import pygame
import sys
from Creature import Creature
from Food import Food

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

BLACK = (0, 0, 0)

# Create screen
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Evolution Simulation")

# Clock for controlling framerate
clock = pygame.time.Clock()
FPS = 60

creature_population = []
creature_population.append(Creature(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

food_population = []
food_population.append(Food(100, 100))

# Main update loop
running = True
while running:

    dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(BLACK)
    
    # Update creatures
    for creature in creature_population:
        creature.update(dt)

    # Get new creatures (if any)
    new_creatures = []
    for creature in creature_population:
        if creature.can_reproduce():
            child = creature.clone()
            child.mutate()
            new_creatures.append(child)
    creature_population += new_creatures

    # Draw food
    for food in food_population:
        food.draw(screen)
    
    # Draw creatures
    for creature in creature_population:
        creature.draw(screen)

    pygame.display.flip()    
    clock.tick(FPS)

pygame.quit()
sys.exit()