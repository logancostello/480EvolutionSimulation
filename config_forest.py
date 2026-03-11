# Single file for all hyperparameters
# Simulation details can be tuned here
# Sharing a copy of this file (along with a seed) makes simulations shareable
# SEED = 2420520844
# ---------- Simulation ---------- 
SIMULATION_WIDTH = 12000
SIMULATION_HEIGHT = 8000
NUM_INIT_CREATURE = 75
NUM_INIT_FOOD = 500

# ---------- Food ----------
ENERGY_DENSITY = 0.40
FOOD_RADIUS = 10
NUM_INIT_FORESTS = 3
WORLD_SPAWN_WEIGHT = 1  # relative weight for open-world spawning
FOREST_SPAWN_WEIGHT_MIN = 5 # relative min weight for forest spawn
FOREST_SPAWN_WEIGHT_MAX = 10  # relative max weight for forest spawn
FOREST_MIN_SIZE = 0.25 # 0-1 indicating % of world
FOREST_MAX_SIZE = 0.4 # 0-1 indicating % of world

# ---------- Genetics ----------
# Also see the Genome.py file for specific gene details
DEFAULT_MUTATION_RATE = 0.2 # chance of mutation
DEFAULT_MUTATION_STRENGTH = 0.1 # max % change due to mutation

# ---------- Energy ----------
DEFAULT_MAX_ENERGY = 60
BASAL_METABOLIC_RATE_ENERGY_PENALTY = 0.6
MOVEMENT_ENERGY_PENALTY = 0.75
SENSORY_ENERGY_PENALTY = 0.25
NUM_BRAIN_NODES_ENERGY_PENALTY = 0.01
NUM_BRAIN_CONNECTION_ENERGY_PENALTY = 0.01

# ---------- Collisions ----------
DAMAGE_SCALAR = 0.075

# ---------- Brain ----------
NUM_INPUTS = 13
NUM_OUTPUTS = 3

NEW_WEIGHT_MEAN = 0
NEW_WEIGHT_SD = 0.5

INIT_CONNECTION_RATE = 0.5
NUM_VALID_MUTATION_ATTEMPTS = 10

ANY_WEIGHT_MUTATION_RATE = 0.8
WEIGHT_MUTATION_RATE = 0.33
WEIGHT_SIGN_FLIP_MUTATION_RATE = 0.1
NEW_EDGE_MUTATION_RATE = 0.33
NEW_NODE_MUTATION_RATE = 0.1
REMOVE_NODE_MUTATION_RATE = 0.1
REMOVE_EDGE_MUTATION_RATE = 0.33

WEIGHT_MUTATION_MEAN = 0
WEIGHT_MUTATION_SD = 0.25