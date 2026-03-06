# Single file for all hyperparameters
# Simulation details can be tuned here
# Sharing a copy of this file (along with a seed) makes simulations shareable

# ---------- Simulation ----------
SIMULATION_WIDTH = 12000
SIMULATION_HEIGHT = 8000
NUM_INIT_CREATURE = 75
NUM_INIT_FOOD = 500

# ---------- Food ----------
ENERGY_DENSITY = 0.20
FOOD_RADIUS = 10
NUM_INIT_FORESTS = 0
WORLD_SPAWN_WEIGHT = 3  # relative weight for open-world spawning
FOREST_SPAWN_WEIGHT_MIN = 3 # relative min weight for forest spawn
FOREST_SPAWN_WEIGHT_MAX = 5.5  # relative max weight for forest spawn
FOREST_MIN_SIZE = 0.1 # 0-1 indicating % of world
FOREST_MAX_SIZE = 0.25 # 0-1 indicating % of world

# ---------- Genetics ----------
# Also see the Genome.py file for specific gene details
DEFAULT_MUTATION_RATE = 0.2 # chance of mutation
DEFAULT_MUTATION_STRENGTH = 0.1 # max % change due to mutation

# ---------- Energy ----------
DEFAULT_MAX_ENERGY = 60
BASAL_METABOLIC_RATE_ENERGY_PENALTY = 0.3
MOVEMENT_ENERGY_PENALTY = 0.6
SENSORY_ENERGY_PENALTY = 0.2
NUM_BRAIN_NODES_ENERGY_PENALTY = 0.04
NUM_BRAIN_CONNECTION_ENERGY_PENALTY = 0.01

# ---------- Collisions ----------
DAMAGE_SCALAR = 0.1
