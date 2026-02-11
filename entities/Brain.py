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
            self.add_random_node()

        if random.random() < REMOVE_NODE_MUTATION_RATE:
            self.remove_random_node()
        
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

            # check if connection will create a cycle
            if self.creates_cycle(from_node, to_node):
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

    def add_random_node(self):
        """ Randomly split an existing connection with a new node """

        if len(self.connections.keys()) == 0: 
            return
        
        from_node, to_node = random.choice(list(self.connections.keys()))
        connection_weight = self.connections[(from_node, to_node)]
        new_node = max(self.nodes) + 1

        self.nodes.append(new_node)
        del self.connections[(from_node, to_node)]

        if random.random() < 0.5:
            self.connections[(from_node, new_node)] = connection_weight
            self.connections[(new_node, to_node)] = 1
        else:
            self.connections[(from_node, new_node)] = 1
            self.connections[(new_node, to_node)] = connection_weight

    def remove_random_node(self):
        """ Randomly removes an inner node, keeping either its in edge or out edge """

        # Ensure inner nodes exist
        if len(self.nodes) == self.n_inputs + self.n_outputs:
            return 
        
        node_to_remove = random.choice(self.nodes[self.n_inputs + self.n_outputs:])

        # Get all edges into and out of node
        in_nodes = []
        out_nodes = []
        for from_node, to_node in self.connections:
            if from_node == node_to_remove:
                out_nodes.append(to_node)

            elif to_node == node_to_remove:
                in_nodes.append(from_node)

        # Connect parents of the node to the children of the node
        for in_node in in_nodes:
            for out_node in out_nodes:

                if (in_node, out_node) in self.connections:
                    continue

                if random.random() < 0.5:
                    self.connections[(in_node, out_node)] = self.connections[(in_node, node_to_remove)]
                else:
                    self.connections[(in_node, out_node)] = self.connections[(node_to_remove, out_node)]

        # Remove node and edges to it
        self.nodes.remove(node_to_remove)
        for in_node in in_nodes:
            del self.connections[(in_node, node_to_remove)]
        for out_node in out_nodes:
            del self.connections[(node_to_remove, out_node)]


    def topological_sort(self):
        """ Orders nodes such that a node's parents come before it """
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

    def creates_cycle(self, from_node, to_node):
        """ Checks if adding a connection will create a cycle """

        # Get all to_node neighbors 
        neighbors = []
        for f_node, t_node in self.connections:
            if f_node != to_node:
                continue
            
            if t_node == from_node:
                return True
            
            neighbors.append(t_node)

        # No neighbors are from_node, check if neighbors can reach from_node 
        for neighbor in neighbors:
            if self.creates_cycle(from_node, neighbor):
                return True
            
        return False
