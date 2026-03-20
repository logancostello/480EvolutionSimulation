# CSC480 Evolution Simulation
By Logan Costello, Rachel Hartfelder, Ainsley Forster, and Joshua Livergood

This is a our project for Dr. Canaan's CSC 480 class.

The primary source of inspiration for this project is [The Bibites](https://www.thebibites.com/?v=0b3b97fa6688), which is an advanced evolution simulation.

## Running the Simulation
In order to run the project, adjust the values in ```config.py``` to your liking, then run ```python main.py```. 
Additionally, you can run the simulation with a seed. For example, ```python main.py 1234```

While the simulation is running:
- Press ```space``` to pause/play
- Press ```a``` to run the simulation at max speed
- Press ```m``` to toggle the menu on and off

After running the simulation, the resulting data will be stored in the ```data/``` folder. Charts and figures can be 
generated in the ```analytics/analytics.ipynb``` file

## Report Reproduction
In order to reproduce the results in our report, use the following settings at the top of the config.py file and do not 
modify any other inputs. Our results are based primarily on SEED 325, and compared to results of SEED 739.

### Desert Simulation: Scenario 1
SEED = 325  # 325 or 739

IS_FOREST = False

DAMAGE_SCALAR = 0.0

IS_LIMITED = True

NUM_INPUTS = 10

### Desert Simulation: Scenario 2
SEED = 325  # 325 or 739

IS_FOREST = False

DAMAGE_SCALAR = 0.2

IS_LIMITED = True

NUM_INPUTS = 10

### Desert Simulation: Scenario 3
SEED = 325  # 325 or 739

IS_FOREST = False

DAMAGE_SCALAR = 0.2

IS_LIMITED = False

NUM_INPUTS = 16

### Forest Simulation: Scenario 1
SEED = 325  # 325 or 739

IS_FOREST = True

DAMAGE_SCALAR = 0.0

IS_LIMITED = True
NUM_INPUTS = 10

### Forest Simulation: Scenario 2
SEED = 325  # 325 or 739

IS_FOREST = True

DAMAGE_SCALAR = 0.2

IS_LIMITED = True

NUM_INPUTS = 10

### Forest Simulation: Scenario 3
SEED = 325  # 325 or 739

IS_FOREST = True

DAMAGE_SCALAR = 0.2

IS_LIMITED = False

NUM_INPUTS = 16
