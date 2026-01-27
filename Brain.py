import random
import math 

NEW_WEIGHT_MEAN = 0
NEW_WEIGHT_SD = 0.5

class Brain:
    def __init__(self, n_inputs, n_outputs):
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        self.next_node_id = n_inputs + n_outputs

        self.topological_order = [i for i in range(n_inputs + n_outputs)]
        self.connections = {} # (from, to) -> weight

        self.initialize_connections()

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
