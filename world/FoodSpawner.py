import random
from entities.Food import Food
from entities.Food import ENERGY_DENSITY
from spacial.Point import Point
from entities.Forest import Forest
from config import (
    FOOD_RADIUS,
    NUM_INIT_FORESTS,
    WORLD_SPAWN_WEIGHT,
    FOREST_SPAWN_WEIGHT_MIN,
    FOREST_SPAWN_WEIGHT_MAX,
    FOREST_MAX_SIZE, 
    FOREST_MIN_SIZE
)

class FoodSpawner:
    def __init__(self, simulation, target_food_count):
        self.sim = simulation
        self.target_food_count = target_food_count
        self.forests = []
        self._world_weight = WORLD_SPAWN_WEIGHT

    @property
    def _total_weight(self):
        """Sum of all forest weights plus the open-world weight."""
        return sum(f.weight for f in self.forests) + self._world_weight

    def initialize_forests(self):
        """Create forests spread across the world."""
        avg_world_size = (self.sim.simulation_width + self.sim.simulation_height) / 2
        min_radius = int(avg_world_size * FOREST_MIN_SIZE)
        max_radius = int(avg_world_size * FOREST_MAX_SIZE)
        max_attempts_per_forest = 50

        for _ in range(NUM_INIT_FORESTS):
            best_pos = self._find_best_forest_position(max_attempts_per_forest)
            wt = random.uniform(FOREST_SPAWN_WEIGHT_MIN, FOREST_SPAWN_WEIGHT_MAX)
            r_x = random.randint(min_radius, max_radius)
            r_y = random.randint(min_radius, max_radius)
            self.forests.append(Forest(best_pos, wt, r_x, r_y))

    def initialize_food(self):
        """Generate initial food distribution across forests and world."""
        for forest in self.forests:
            food_count = round(self.target_food_count * (forest.weight / self._total_weight))
            for _ in range(food_count):
                pos = self._spawn_point_in_forest(forest)
                self.sim.food.insert(Food(pos, FOOD_RADIUS))

        leftover_food = self.target_food_count - len(self.sim.food.get_all())
        for _ in range(leftover_food):
            pos = self._spawn_random_point()
            self.sim.food.insert(Food(pos, FOOD_RADIUS))

    def spawn_food(self):
        """Spawn food to maintain target count."""
        food_energy = ENERGY_DENSITY * FOOD_RADIUS ** 2

        while self.sim.energy_pool >= food_energy:
            pos = self._choose_spawn_position()
            self.sim.food.insert(Food(pos, FOOD_RADIUS))
            self.sim.energy_pool -= food_energy

    # --- private helpers ---

    def _find_best_forest_position(self, max_attempts):
        """Pick the candidate position that maximises distance from existing forests."""
        best_pos = None
        best_distance = 0

        for _ in range(max_attempts):
            candidate = self._spawn_random_point()

            if not self.forests:
                return candidate

            min_dist = min(
                ((candidate.x - f.position.x) ** 2 + (candidate.y - f.position.y) ** 2) ** 0.5
                for f in self.forests
            )

            if min_dist > best_distance:
                best_distance = min_dist
                best_pos = candidate

        return best_pos

    def _choose_spawn_position(self):
        """Choose a spawn position weighted by forest density vs open world."""
        r = random.random() * self._total_weight
        cumulative = 0

        for forest in self.forests:
            cumulative += forest.weight
            if r < cumulative:
                return self._spawn_point_in_forest(forest)

        return self._spawn_random_point()

    def _spawn_random_point(self):
        x = self.sim.simulation_width * random.random()
        y = self.sim.simulation_height * random.random()
        return Point(x, y)

    def _spawn_point_in_forest(self, forest):
        """Recursively find a valid point within a forest ellipse."""
        x = forest.position.x + random.randint(-forest.radius_x, forest.radius_x)
        y = forest.position.y + random.randint(-forest.radius_y, forest.radius_y)

        if 0 < x < self.sim.simulation_width and 0 < y < self.sim.simulation_height:
            nx = (x - forest.position.x) / forest.radius_x
            ny = (y - forest.position.y) / forest.radius_y
            norm = nx * nx + ny * ny

            if norm > 1.0:
                return self._spawn_point_in_forest(forest)

            if (norm ** 0.5) <= 0.75:
                return Point(x, y)
            elif random.randint(0, 2) == 0:
                return Point(x, y)

        return self._spawn_point_in_forest(forest)