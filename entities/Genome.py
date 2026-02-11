import random

DEFAULT_MUTATION_RATE = 0.2 # chance of mutation
DEFAULT_MUTATION_STRENGTH = 0.1 # max % change due to mutation

class Genome:

    # Stores metadata for each gene
    # {gene_name: {default, min, max, mutation_rate, mutation_strength}}
    gene_metadata = {}

    def __init__(self, **gene_values):
        """ Not directly called. Instead used by create_default """
        for gene, value in gene_values.items():
            setattr(self, gene, value)

    @classmethod
    def create_default(cls):
        """ Class method. Returns genome object with default values """
        values = {name: metadata["default"] for name, metadata in cls.gene_metadata.items()}
        return cls(**values)

    @classmethod
    def register_gene(cls, name, default, min, max, mutation_rate=DEFAULT_MUTATION_RATE, mutation_strength=DEFAULT_MUTATION_STRENGTH):
        """ Class method. Adds gene to genome metadata """
        cls.gene_metadata[name] = {
            "default": default,
            "min": min,
            "max": max,
            "mutation_rate": mutation_rate,
            "mutation_strength": mutation_strength
        }

    def clone(self):
        """ Return genome with identical values as current """
        values = {name: getattr(self, name) for name in self.gene_metadata}
        return Genome(**values)
    
    def mutate(self):
        """
        Randomly mutate the values of each gene
        Mutations are Normal with standard deviation = range * mutation_strength.
        Values are clamped to [min, max] after mutation.
        """
        for name, metadata in self.gene_metadata.items():
            if random.random() < metadata["mutation_rate"]:
                current = getattr(self, name)
                gene_range = metadata["max"] - metadata["min"]
                delta = random.gauss(0, gene_range * metadata["mutation_strength"])
                new_value = current + delta
                new_value = max(metadata["min"], min(metadata["max"], new_value))
                setattr(self, name, new_value)

Genome.register_gene(name="max_speed", default=100, min=1, max=300) # pixels per second
Genome.register_gene(name="max_turn_rate", default=3.14, min=1, max=6.28) # radians per second
Genome.register_gene(name="radius", default=25, min=1, max=50) # pixels
Genome.register_gene(name="time_between_reproduction", default=20, min=20, max=120) # seconds
Genome.register_gene(name="energy_for_reproduction", default=15, min=15, max=60) # energy
Genome.register_gene(name="viewable_distance", default=150, min=1, max=500) # pixels
Genome.register_gene(name="fov", default=1.57, min=1, max=6.28) # radians
Genome.register_gene(name="init_energy", default=30, min=30, max=30) # seconds of survival
Genome.register_gene(name="color_r", default=255, min=75, max=255, mutation_rate=0.05, mutation_strength=0.1) # red component of color
Genome.register_gene(name="color_g", default=255, min=0, max=80, mutation_rate=0.05, mutation_strength=0.1) # green component of color
Genome.register_gene(name="color_b", default=255, min=75, max=255, mutation_rate=0.05, mutation_strength=0.1) # blue component of color