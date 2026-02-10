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
            "min_value": min,
            "max_value": max,
            "mutation_rate": mutation_rate,
            "mutation_strength": mutation_strength
        }

Genome.register_gene(name="max_speed", default=100, min=0, max=300) # pixels per second
Genome.register_gene(name="max_turn_rate", default=3.14, min=0, max=6.28) # radians per second
Genome.register_gene(name="radius", default=25, min=1, max=50) # pixels
Genome.register_gene(name="time_between_reproduction", default=20, min=10, max=120) # seconds
Genome.register_gene(name="energy_for_reproduction", default=15, min=1, max=60) # energy
Genome.register_gene(name="viewable_distance", default=150, min=0, max=500) # pixels
Genome.register_gene(name="fov", default=1.57, min=0, max=6.28) # radians
Genome.register_gene(name="init_energy", default=30, min=1, max=100) # seconds of survival
Genome.register_gene(name="color_r", default=255, min=0, max=255, mutation_rate=0) # red component of color
Genome.register_gene(name="color_g", default=255, min=0, max=255, mutation_rate=0) # green component of color
Genome.register_gene(name="color_b", default=255, min=0, max=255, mutation_rate=0) # blue component of color