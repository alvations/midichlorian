import random
import datetime
from bisect import bisect_left
from math import exp

class Chromosome:
    __slots__ = ['genes', 'fitness', 'age', 'strategy']
    def __init__(self, genes, fitness, age=None, strategy=None):
        self.genes = genes
        self.fitness = fitness
        self.strategy = strategy
        self.age = age

class Mutation:
    def __init__(self, mutation_type):
        # Select the mutation strategy.
        self.mutate = {'pick': self.pick, 'swap': self.swap}[mutation_type]

    def pick(self, parent, gene_set, fitness_func, *args, **kwargs):
        """
        :param parent:
        :type parent: Chromosome
        :rtype: Chromosome
        """
        child_genes = list(parent.genes)
        index = random.randrange(0, len(parent.genes))
        new_gene, alternate = random.sample(gene_set, 2)
        child_genes[index] = alternate if new_gene == child_genes[index] else new_gene
        return Chromosome(child_genes, fitness_func(child_genes, *args, **kwargs), age=parent.age)

    def swap(self, parent, gene_set, fitness_func, *args, **kwargs):
        """
        :param parent:
        :type parent: Chromosome
        :rtype: Chromosome
        """
        gene_indices = list(range(len(gene_set)))
        child_genes = list(parent.genes)
        index_a, index_b = random.sample(gene_indices, 2)
        child_genes[index_a],  child_genes[index_b] = child_genes[index_b], child_genes[index_a]
        return Chromosome(child_genes, fitness_func(child_genes, *args, **kwargs), age=parent.age)


class Evolution:
    def __init__(self, gene_set, fitness_func, optimal_fitness, mutation,
                 *args, **kwargs):
        self.gene_set = gene_set
        self.fitness_func = fitness_func
        self.optimal_fitness = optimal_fitness
        # Select the mutation strategy.
        self.mutation = mutation
        # Currently *gene_indices* are only used for swap mutation


    def generate_parent(self, num_genes, age=None, *args, **kwargs):
        genes = []
        while len(genes) < num_genes:
            sample_size = min(num_genes-len(genes), len(self.gene_set))
            genes.extend(random.sample(self.gene_set, sample_size))
        return Chromosome(genes, self.fitness_func(genes, *args, **kwargs),
                          age, strategy='create')

    def child_becomes_parent(self, child_fitness, fitness_history):
        # Determine how far away is the child_fitness from best_fitness.
        # Find the  position of the child's fitness.
        index = bisect_left(fitness_history, child_fitness, 0, len(fitness_history))
        # Find the proxmity to the best fitness (last on the *fitness_history*)
        difference = len(fitness_history) - index
        # Convert it to a proportion.
        similar_proportion = difference / len(fitness_history)
        # Pick a random number, check if random number is smaller than
        # `exp(-similar_proportion)`, then child becomes parent.
        return random.random() < exp(-similar_proportion)

    def evolve(self, parent, max_age=None, *args, **kwargs):
        fitness_history = [parent.fitness]
        best_parent = parent
        while True:
            child = self.mutation.mutate(parent, self.gene_set, self.fitness_func,
                                         *args, **kwargs)

            # parent's fitness > child's fitness
            if parent.fitness > child.fitness:
                if max_age is None:
                    continue
                # Let the parent die out if max_age is reached.
                parent.age += 1
                if max_age > parent.age:
                    continue
                # Simulated annealing.
                # If child is to become the new parent.
                if self.child_becomes_parent(child.fitness, fitness_history):
                    parent = child
                else: # Otherwise reset parent's age.
                    best_parent.age = 0
                    parent = best_parent
                continue

            # parent's fitness == child's fitness
            if child.fitness == parent.fitness:
                child.age = parent.age + 1
                parent = child
                continue

            # parent's fitness < child's fitness:
            child.age = 0
            parent = child

            # best_parent's fitness < child's fitness:
            if child.fitness > best_parent.fitness:
                best_parent = child
                yield best_parent
                fitness_history.append(child.fitness)

    def find_fittest(self, num_genes, random_seed=0, max_age=None, *args, **kwargs):
        random.seed(random_seed)
        # Genesis: Create generation 0 parent.
        gen0 = self.generate_parent(num_genes, age=0, *args, **kwargs)
        # If somehow, we met the criteria after gen0, banzai!
        if gen0.fitness > self.optimal_fitness:
            return best_parent

        start_time = datetime.datetime.now()
        for child in self.evolve(gen0, max_age, *args, **kwargs):
            # Log time taken to reach better fitness.
            time_taken = datetime.datetime.now() - start_time
            print("{}\t{}\t{}".format(child.genes, child.fitness, time_taken))
            # Return child if fitness reached optimal.
            if self.optimal_fitness <= child.fitness:
                return child
