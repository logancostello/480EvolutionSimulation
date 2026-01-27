import random
import math 

NEW_WEIGHT_MEAN = 0
NEW_WEIGHT_SD = 0.5

ANY_WEIGHT_MUTATION_RATE = 0.8
WEIGHT_MUTATION_RATE = 0.33
WEIGHT_SIGN_FLIP_MUTATION_RATE = 0.1
NEW_EDGE_MUTATION_RATE = 0.33
NEW_NODE_MUTATION_RATE = 0.1
REMOVE_NODE_MUTATION_RATE = 0.1

WEIGHT_MUTATION_MEAN = 0
WEIGHT_MUTATION_SD = 0.25

class Brain:
    def __init__(self, n_inputs, n_outputs):
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        self.next_node_id = n_inputs + n_outputs

        self.topological_order = [i for i in range(n_inputs + n_outputs)]
        self.connections = {} # (from, to) -> weight

        self.initialize_connections()

    def clone(self):
        """ Return deep copy of brain """
        new_brain = Brain(self.n_inputs, self.n_outputs)
        new_brain.next_node_id = self.next_node_id
        new_brain.topological_order = list(self.topological_order)
        new_brain.connections = dict(self.connections)
        return new_brain

    def initialize_connections(self):
        """ Connect every input node to every output node with a random connection """
        for i in range(self.n_inputs):
            for o in range(self.n_inputs, self.n_inputs + self.n_outputs):
                self.connections[(i, o)] = random.gauss(NEW_WEIGHT_MEAN, NEW_WEIGHT_SD)
    

    def think(self, inputs):
        """ Calculate output nodes """
        assert len(inputs) == self.n_inputs

        node_values = {}

        for i in range(self.n_inputs):
            node_values[i] = inputs[i]

        for node_idx in self.topological_order:

            if node_idx < self.n_inputs:
                continue

            total = 0.0
            for (from_node, to_node), weight in self.connections.items():
                if to_node == node_idx:
                    total += node_values[from_node] * weight
            
            node_values[node_idx] = math.tanh(total)

        outputs = []
        for node_idx in range(self.n_inputs, self.n_inputs + self.n_outputs):
            outputs.append(node_values[node_idx])

        return outputs
    
    def mutate(self):
        """ Mutate the brain by adjusting topology and weights """ 
        if random.random() < ANY_WEIGHT_MUTATION_RATE:
            self.mutate_weights()
        
        if random.random() < NEW_EDGE_MUTATION_RATE:
            # todo
            pass

        if random.random() < NEW_NODE_MUTATION_RATE:
            # todo
            pass

        if random.random() < REMOVE_NODE_MUTATION_RATE:
            # todo
            pass


    def mutate_weights(self):
        for key in self.connections:
            if random.random() < WEIGHT_MUTATION_RATE:
                self.connections[key] += random.gauss(WEIGHT_MUTATION_MEAN, WEIGHT_MUTATION_SD)

            elif random.random() < WEIGHT_SIGN_FLIP_MUTATION_RATE:
                self.connections[key] *= -1
    
