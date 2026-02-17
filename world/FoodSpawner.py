import random
from entities.Food import Food
from spacial.Point import Point
from entities.Forest import Forest

NUM_INIT_FORESTS = 5
MAX_FOOD_RADIUS = 10

class FoodSpawner:
    def __init__(self, simulation, target_food_count):
        self.sim = simulation
        self.target_food_count = target_food_count
        self.forests = []
        self.total_forest_weights = 2  # starting number is the likelihood of food appearing outside a forest
    
    def initialize_forests(self):
        """Create forests in the world"""
        for _ in range(NUM_INIT_FORESTS):
            pt = self._spawn_random_point()
            wt = random.randint(1, 3)
            r_x = random.randint(500, 1500)
            r_y = random.randint(500, 1500)
            self.forests.append(Forest(pt, wt, r_x, r_y))
            self.total_forest_weights += wt
    
    def initialize_food(self):
        """Generate initial food distribution across forests and world"""
        # Generate food within forests
        for forest in self.forests:
            food_count = round(self.target_food_count * (forest.weight / self.total_forest_weights))
            for _ in range(food_count):
                pos = self._spawn_point_in_forest(forest)
                self.sim.food.insert(Food(pos, MAX_FOOD_RADIUS))
        
        # Generate additional food throughout world
        leftover_food = self.target_food_count - len(self.sim.food.get_all())
        for _ in range(leftover_food):
            pos = self._spawn_random_point()
            self.sim.food.insert(Food(pos, MAX_FOOD_RADIUS))
    
    def spawn_food(self):
        """Spawns food to maintain target count. Call once per frame."""
        food_alive = 0
        for f in self.sim.food.get_all():
            if f.is_alive():
                food_alive += 1

        food_to_spawn = self.target_food_count - food_alive

        for _ in range(food_to_spawn):
            pos = self._choose_spawn_position()
            self.sim.food.insert(Food(pos, MAX_FOOD_RADIUS))
    
    def _choose_spawn_position(self):
        """Choose spawn position weighted by forest density"""
        r = random.random()
        cumulative = 0

        for forest in self.forests:
            cumulative += forest.weight / self.total_forest_weights
            if r < cumulative:
                return self._spawn_point_in_forest(forest)
        
        # No forest chosen, spawn randomly in world
        return self._spawn_random_point()
    
    def _spawn_random_point(self):
        x = self.sim.simulation_width * random.random()
        y = self.sim.simulation_height * random.random()
        return Point(x, y)
    
    def _spawn_point_in_forest(self, forest):
        """Recursively find valid point within forest ellipse"""
        x = forest.position.x + random.randint(-forest.radius_x, forest.radius_x)
        y = forest.position.y + random.randint(-forest.radius_y, forest.radius_y)

        if 0 < x < self.sim.simulation_width and 0 < y < self.sim.simulation_height:
            # normalized distance from forest center
            nx = (x - forest.position.x) / forest.radius_x
            ny = (y - forest.position.y) / forest.radius_y
            norm = nx * nx + ny * ny

            if norm > 1.0:  # outside of ellipse
                return self._spawn_point_in_forest(forest)

            if (norm ** 0.5) <= 0.75:  # accept all points in inner 75% of forest
                return Point(x, y)
            elif random.randint(0, 2) == 0:  # 1/3 as likely in outer 25% of forest
                return Point(x, y)

        return self._spawn_point_in_forest(forest)