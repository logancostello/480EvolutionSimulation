import random
from entities.Food import Food
from entities.Food import ENERGY_DENSITY
from spacial.Point import Point
from entities.Forest import Forest

NUM_INIT_FORESTS = 10
MAX_FOOD_RADIUS = 10

class FoodSpawner:
    def __init__(self, simulation, target_food_count):
        self.sim = simulation
        self.target_food_count = target_food_count
        self.forests = []
        self.total_forest_weights = 3  # starting number is the likelihood of food appearing outside a forest
    
    def initialize_forests(self):
        """Create forests in the world"""
        # Scale forest size based on world dimensions
        avg_world_size = (self.sim.simulation_width + self.sim.simulation_height) / 2
        min_radius = int(avg_world_size * 0.10)  # 10% of average world size
        max_radius = int(avg_world_size * 0.25)  # 25% of average world size
        
        max_attempts_per_forest = 50  # Try up to 50 times to find a good spot
        
        for _ in range(NUM_INIT_FORESTS):
            best_pos = None
            best_distance = 0
            
            # Try multiple positions and pick the one farthest from existing forests
            for attempt in range(max_attempts_per_forest):
                candidate_pos = self._spawn_random_point()
                
                if len(self.forests) == 0:
                    # First forest, just place it
                    best_pos = candidate_pos
                    break
                
                # Calculate minimum distance to any existing forest
                min_dist_to_existing = float('inf')
                for existing_forest in self.forests:
                    dx = candidate_pos.x - existing_forest.position.x
                    dy = candidate_pos.y - existing_forest.position.y
                    dist = (dx * dx + dy * dy) ** 0.5
                    min_dist_to_existing = min(min_dist_to_existing, dist)
                
                # Keep track of the position with maximum separation
                if min_dist_to_existing > best_distance:
                    best_distance = min_dist_to_existing
                    best_pos = candidate_pos
            
            # Create forest at best position found
            wt = random.uniform(0, 1)  
            r_x = random.randint(min_radius, max_radius)
            r_y = random.randint(min_radius, max_radius)
            self.forests.append(Forest(best_pos, wt, r_x, r_y))
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
        """ Spawns food to maintain target count"""
        food_energy = ENERGY_DENSITY * MAX_FOOD_RADIUS ** 2
    
        while self.sim.energy_pool >= food_energy:
            pos = self._choose_spawn_position()
            self.sim.food.insert(Food(pos, MAX_FOOD_RADIUS))
            self.sim.energy_pool -= food_energy

    
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