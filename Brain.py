import random
import math 
from collections import Counter

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

class Brain:
    def __init__(self, n_inputs, n_outputs):
        self.n_inputs = n_inputs
        self.n_outputs = n_outputs
        self.nodes = list(range(n_inputs + n_outputs))

        self.topological_order = [i for i in range(n_inputs + n_outputs)]
        self.connections = {} # (from, to) -> weight

        self.initialize_connections()

    def clone(self):
        """ Return deep copy of brain """
        new_brain = Brain(self.n_inputs, self.n_outputs)
        new_brain.nodes = list(self.nodes)
        new_brain.topological_order = list(self.topological_order)
        new_brain.connections = dict(self.connections)
        return new_brain

    def initialize_connections(self):
        """ Randomly make connections from input nodes to output nodes """
        num_possible_connections = self.n_inputs * self.n_outputs
        num_connections_to_create = int(num_possible_connections * INIT_CONNECTION_RATE)
        for _ in range(num_connections_to_create):
            self.add_random_connection()
    

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
            self.add_random_connection()

        if random.random() < REMOVE_EDGE_MUTATION_RATE:
            self.remove_random_connection()

        if random.random() < NEW_NODE_MUTATION_RATE:
            # todo
            pass

        if random.random() < REMOVE_NODE_MUTATION_RATE:
            # todo
            pass
        
        # Resort nodes for correct order of computation when thinking
        self.topological_sort()

    def mutate_weights(self):
        """ Randomly mutate the weights of brain connections """
        for key in self.connections:
            if random.random() < WEIGHT_MUTATION_RATE:
                self.connections[key] += random.gauss(WEIGHT_MUTATION_MEAN, WEIGHT_MUTATION_SD)

            elif random.random() < WEIGHT_SIGN_FLIP_MUTATION_RATE:
                self.connections[key] *= -1

    def add_random_connection(self):
        """ Randomly add a connection in the brain """
        for _ in range(NUM_VALID_MUTATION_ATTEMPTS):

            # pick two random nodes
            from_node = random.choice(self.nodes)
            to_node = random.choice(self.nodes)

            # check for connection from output node
            if self.n_inputs <= from_node < self.n_inputs + self.n_outputs:
                continue

            # check for connection to input node
            if to_node < self.n_inputs:
                continue

            # check for self connection
            if to_node == from_node:
                continue

            # check if connection already exists
            if (from_node, to_node) in self.connections:
                continue

            # add new connection
            weight = random.gauss(NEW_WEIGHT_MEAN, NEW_WEIGHT_SD)
            self.connections[(from_node, to_node)] = weight
            return
        
    def remove_random_connection(self):
        """ Randomly remove a connection from the brain """
        if len(self.connections.keys()) == 0: 
            return
         
        random_key = random.choice(list(self.connections.keys()))
        del self.connections[random_key]

    def topological_sort(self):

        num_incoming_edges = Counter()
        for (from_node, to_node) in self.connections:
            num_incoming_edges[to_node] += 1

        no_incoming_edges = set()
        for node in self.nodes:
            if num_incoming_edges[node] == 0:
                no_incoming_edges.add(node)

        topological_order = []

        while len(no_incoming_edges) > 0:
            node = no_incoming_edges.pop()
            topological_order.append(node)

            for (from_node, to_node) in self.connections:
                if from_node != node:
                    continue
                
                num_incoming_edges[to_node] -= 1
                if num_incoming_edges[to_node] == 0:
                    no_incoming_edges.add(to_node)

        self.topological_order = topological_order

