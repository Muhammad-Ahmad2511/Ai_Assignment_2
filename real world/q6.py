import random
import math

demands = [12,45,23,67,34,19,
           56,38,72,15,49,61,
           27,83,41,55,30,77,
           64,18,52,39,71,26,
           44,91,33,58,22,85,
           16,69,47,74,31,53]

supply_penalty = 5
num_drivers = 10
grid_size = 6

# ─── PART (a) ───

def state_fitness(state, demands):
    return sum(demands[i] for i in state) - supply_penalty * num_drivers

def get_neighbours(state):
    placed = state
    unplaced = set(range(36)) - placed
    neighbours = []
    for zone_out in placed:
        for zone_in in unplaced:
            neighbour = (placed - {zone_out}) | {zone_in}
            neighbours.append(neighbour)
    return neighbours

def random_state():
    return set(random.sample(range(36), num_drivers))

print("=" * 60)
print("PART (a): Foundation")
print("=" * 60)

random.seed(42)
for i in range(3):
    s = random_state()
    neighbours = get_neighbours(s)
    print(f"Random state {i+1}: {sorted(s)}")
    print(f"  Fitness: {state_fitness(s, demands)}")
    print(f"  Number of neighbours: {len(neighbours)}")
    # verify all neighbours have size 10 and no duplicates
    for n in neighbours:
        assert len(n) == 10
    print(f"  Verification passed: all neighbours have size 10, no duplicates")

# ─── PART (b) ───

def hc_driver(state, demands, variant):
    current = state
    current_fitness = state_fitness(current, demands)
    steps = 0

    while True:
        neighbours = get_neighbours(current)
        if variant == 'first_choice':
            moved = False
            for nb in neighbours:
                nb_fitness = state_fitness(nb, demands)
                if nb_fitness > current_fitness:
                    current = nb
                    current_fitness = nb_fitness
                    steps += 1
                    moved = True
                    break
            if not moved:
                break
        elif variant == 'stochastic':
            improving = [nb for nb in neighbours if state_fitness(nb, demands) > current_fitness]
            if not improving:
                break
            current = random.choice(improving)
            current_fitness = state_fitness(current, demands)
            steps += 1

    return current, current_fitness, steps

def rrhc_driver(num_restarts, demands, variant):
    best_state = None
    best_fitness = float('-inf')
    per_restart_best = []

    for _ in range(num_restarts):
        init = random_state()
        state, fitness, _ = hc_driver(init, demands, variant)
        per_restart_best.append(fitness)
        if fitness > best_fitness:
            best_fitness = fitness
            best_state = state

    return best_state, per_restart_best

print()
print("=" * 60)
print("PART (b): Random Restart Hill Climbing")
print("=" * 60)
print("Variant chosen: first_choice")
print()

random.seed(0)
best_state_rrhc, per_restart = rrhc_driver(30, demands, 'first_choice')
best_fitness_rrhc = state_fitness(best_state_rrhc, demands)

print(f"Best fitness found: {best_fitness_rrhc}")
print(f"Best state (zone indices): {sorted(best_state_rrhc)}")
print("Driver zone assignments:")
for idx in sorted(best_state_rrhc):
    row = idx // grid_size
    col = idx % grid_size
    print(f"  Zone {idx}: (row={row}, col={col}), demand={demands[idx]}")
print(f"Per-restart best fitness: {per_restart}")

# ─── PART (c) ───

def ga_fitness(chromosome, demands):
    return sum(demands[i] for i in chromosome) - supply_penalty * num_drivers

def ordered_crossover(p1, p2):
    n = len(p1)
    start = random.randint(0, n - 2)
    end = random.randint(start + 1, n)
    slice_genes = p1[start:end]
    child = list(slice_genes)
    for gene in p2:
        if len(child) == n:
            break
        if gene not in child:
            child.append(gene)
    return sorted(child)

def ga_mutate(chromosome, p_m):
    if random.random() < p_m:
        all_zones = set(range(36))
        in_chrom = set(chromosome)
        out_zones = list(all_zones - in_chrom)
        idx = random.randint(0, len(chromosome) - 1)
        new_zone = random.choice(out_zones)
        chromosome = chromosome[:]
        chromosome[idx] = new_zone
        chromosome = sorted(set(chromosome))
        # if somehow length changed (shouldn't happen), pad/trim
        while len(chromosome) < num_drivers:
            z = random.choice(list(all_zones - set(chromosome)))
            chromosome.append(z)
            chromosome = sorted(chromosome)
    return chromosome

def tournament_select(population, demands, k=3):
    contestants = random.sample(population, k)
    return max(contestants, key=lambda c: ga_fitness(c, demands))

def run_driver_ga(pop_size, generations, p_m):
    # initialise population
    population = [sorted(random.sample(range(36), num_drivers)) for _ in range(pop_size)]

    best_chromosome = max(population, key=lambda c: ga_fitness(c, demands))
    best_fit = ga_fitness(best_chromosome, demands)

    for _ in range(generations):
        new_pop = []
        while len(new_pop) < pop_size:
            p1 = tournament_select(population, demands)
            p2 = tournament_select(population, demands)
            child = ordered_crossover(p1, p2)
            child = ga_mutate(child, p_m)
            new_pop.append(child)
        population = new_pop
        gen_best = max(population, key=lambda c: ga_fitness(c, demands))
        gen_fit = ga_fitness(gen_best, demands)
        if gen_fit > best_fit:
            best_fit = gen_fit
            best_chromosome = gen_best

    return best_chromosome, best_fit

print()
print("=" * 60)
print("PART (c): Genetic Algorithm")
print("=" * 60)

random.seed(0)
best_chrom, best_fit_ga = run_driver_ga(30, 100, 0.1)

print(f"Best fitness found: {best_fit_ga}")
print(f"Best chromosome: {best_chrom}")
print("Driver zone assignments:")
for idx in best_chrom:
    row = idx // grid_size
    col = idx % grid_size
    print(f"  Zone {idx}: (row={row}, col={col}), demand={demands[idx]}")

# ─── PART (d) ───

def mean(lst):
    return sum(lst) / len(lst)

def std_dev(lst):
    m = mean(lst)
    variance = sum((x - m) ** 2 for x in lst) / len(lst)
    return math.sqrt(variance)

print()
print("=" * 60)
print("PART (d): Head-to-Head Comparison (20 trials each)")
print("=" * 60)

rrhc_results = []
ga_results = []

random.seed(7)
for trial in range(20):
    _, per_restart = rrhc_driver(30, demands, 'first_choice')
    rrhc_results.append(max(per_restart))

random.seed(7)
for trial in range(20):
    _, fit = run_driver_ga(30, 100, 0.1)
    ga_results.append(fit)

print()
print(f"{'Algorithm':<10} {'Mean':>10} {'Std Dev':>10} {'Best':>10}")
print("-" * 44)
print(f"{'RRHC':<10} {mean(rrhc_results):>10.2f} {std_dev(rrhc_results):>10.2f} {max(rrhc_results):>10}")
print(f"{'GA':<10} {mean(ga_results):>10.2f} {std_dev(ga_results):>10.2f} {max(ga_results):>10}")
print()
print("RRHC per-trial results:", rrhc_results)
print("GA per-trial results:", ga_results)