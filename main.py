import numpy as np
import math
import random
import geopy.distance
import networkx as nx
from networkx.algorithms.approximation import clique
import matplotlib.pyplot as plt
import sys

Gen = np.array([])
Fit = np.array([])

max_clique_size = 2

def load_graph(file_name):
  node_count = 0
  graph = []
  with open(file_name) as f:
    for index, line in enumerate(f):
      splited_line = line.strip().split()
      if splited_line[0] == 'e':
        graph.append((int(splited_line[1]), int(splited_line[2])))
      elif splited_line[0] == 'p':
        node_count = int(splited_line[2])
  return graph, node_count

def fitness(graph, individual):

  individual_graph = create_individual_graph(graph, individual)
  sorted_graph_nodes = sorted(individual_graph.degree, key=lambda x: x[1])
  fitness = 0.0
  for node_tuple in sorted_graph_nodes:
    # Checking if nodes create complete graph aka clique
    if nx.density(individual_graph) == 1.0:
      # add found clique size to the fitness variable 
      fitness += len(individual_graph.nodes)
      break
    else:
      fitness -= 1
      individual_graph.remove_node(node_tuple[0])

  return fitness

def create_individual_graph(graph, individual):
  individual_graph = graph.copy()

  individual_index = 0
  for i in graph.nodes:
    if individual[individual_index] == 0:
      individual_graph.remove_node(i)
    individual_index +=1
  
  return individual_graph

def tournament_selection(graph, population):
  new_population = []
  for j in range(2):
    random.shuffle(population)
    for i in range(0, population_size-1, 2):
      if fitness(graph, population[i]) > fitness(graph, population[i+1]):
        new_population.append(population[i])
      else:
        new_population.append(population[i+1])
  return new_population

def roulette_wheel_selection(graph, population):
    new_population = []

    fitness_array = [fitness(graph, c) for c in population]
    min_in_fitness = min(fitness_array)
    fitness_array = [f - min_in_fitness for f in fitness_array]
    max_fitness = sum(fitness_array)

    selection_probs = [f/max_fitness for f in fitness_array]
    for i in range(len(population)):
      new_population.append(population[np.random.choice(len(population), p=selection_probs)])

    return new_population

def create_individual(graph_len):
  individual = []
  for i in range(graph_len):
      individual.append(random.randint(0, 1))
  return individual

def crossover(parent1, parent2, length):
  position = random.randint(2, length-2)
  child1 = parent1[0:position] + parent2[position:length]
  child2 = parent2[0:position] + parent1[position:length]
  return child1, child2

def mutation(individual,probability = 0.6, clique = False):
  length = len(individual)
  check = random.uniform(0, 1)
  if(check <= probability):
      position = random.randint(0, length-1)
      if clique: 
        while(individual[position] == 1):
          position = random.randint(0, length-1)
        # Change value in the position to 1
        individual[position] = 1
      else:
        # Change value to 0 or 1 
        individual[position] = 1 - individual[position]
  return individual

def individual_potential_clique(graph, individual):
  result = []
  clique_size = 0
  individual_index = 0
  for node in graph.nodes:
    if individual[individual_index] == 1:
      clique_size += 1
      result.append(node)
    individual_index += 1
  return result, clique_size

if __name__ == '__main__':
  graph = nx.Graph()

  # graph, node_count = load_graph('low.txt')
  graph_edges, node_count = load_graph('clique.txt')
  graph_nodes = list(range(1, node_count + 1))
  graph.add_nodes_from(graph_nodes)
  graph.add_edges_from(graph_edges)

  # print(list(graph.nodes))
  # nx.draw(graph)
  # plt.show()
  # print(list(nx.find_cliques(graph, [2])))
  # sys.exit()

  generation = 0 
  population_size = 150
  max_generation = 100
  population = []
  graph_len = len(graph)

  for i in range(population_size):
    individual = create_individual(graph_len)
    population.append(individual)


  best_fitness = -999999999999
  fittest_individual = None
  fittest_clique_size = math.inf
  while(generation != max_generation):
    generation += 1
    population = tournament_selection(graph, population)
    # population = roulette_wheel_selection(graph, population)
    random.shuffle(population)
    new_population = []
    for i in range(0, population_size-1, 2):
      child1, child2 = crossover(population[i], population[i+1], graph_len)
      new_population.append(child1)
      new_population.append(child2)

    for individual in new_population:
      if(best_fitness != fittest_clique_size):
          individual = mutation(individual, 0.5)
      else:
        individual = mutation(individual, 0.3)

    population = new_population
    for individual in population:
      local_fitness = fitness(graph, individual)
      if(local_fitness > best_fitness):
          best_fitness = local_fitness
          fittest_individual = individual

    result, fittest_clique_size = individual_potential_clique(graph, fittest_individual)
    if generation % 10 == 0:
      Gen = np.append(Gen, generation)
      Fit = np.append(Fit, best_fitness)
      print("Generation: ", generation, "Best_Fitness: ",
            best_fitness, "Individual: ", result, "Potential Clique Size: ", fittest_clique_size)

  plt.plot(Gen, Fit)
  plt.xlabel("generation")
  plt.ylabel("best-fitness")
  plt.show()

  print("Max clique found by NetworkX heuristic algorithm")
  c = clique.max_clique(graph)
  print(c)
  print(len(c))
