# Genetic algorithm for finding maximum clique in a graph

The fitness function checks whether the subgraph generated from the chromosome creates a clique, if not a node with the slightest degree is deleted from the subgraph, then we look for a clique again.
If a clique is found we add its size to the fitness score.