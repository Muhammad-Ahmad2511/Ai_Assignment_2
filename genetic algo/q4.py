import random
import math

# objective: maximise f(x) = -x^2 + 14x + 5, x in {0..15}
# x represented as 4-bit binary chromosome
# true maximum: x=7, f(7)=54

def decode(chromosome):
    # converts 4-bit binary list to integer
    x = 0
    for bit in chromosome:
        x = x * 2 + bit
    return x


def fitness(chromosome):
    x = decode(chromosome)
    return -x*x + 14*x + 5


def roulette_select(population):
    # fitness proportionate selection using random.random() spin
    fits = [fitness(c) for c in population]
    min_f = min(fits)
    # shift all values positive so selection works correctly
    if min_f < 0:
        adjusted = [f - min_f + 1 for f in fits]
    else:
        adjusted = [f + 1 for f in fits]
    total = sum(adjusted)
    spin = random.random() * total
    cumulative = 0
    for i, af in enumerate(adjusted):
        cumulative += af
        if spin <= cumulative:
            return population[i][:]
    return population[-1][:]


def single_point_crossover(parent1, parent2, point):
    # swap genetic material at given bit position
    offspring1 = parent1[:point] + parent2[point:]
    offspring2 = parent2[:point] + parent1[point:]
    return offspring1, offspring2


def mutate(chromosome, p_m):
    # flip each bit independently with probability p_m
    return [1 - bit if random.random() < p_m else bit
            for bit in chromosome]


# ── part (a) ───

def run_part_a():
    test_chroms = [[0,1,1,0], [1,0,0,1], [1,1,0,0], [0,0,1,1]]

    print("Part (a): decode and fitness tests")
    print(f"{'Chromosome':<20} {'x':>4} {'f(x)':>6}")
    print("-" * 32)
    for c in test_chroms:
        print(f"{str(c):<20} {decode(c):>4} {fitness(c):>6}")

    print("\nRoulette select test (population = above 4 chromosomes):")
    random.seed(0)
    for _ in range(3):
        selected = roulette_select(test_chroms)
        print(f"  selected: {selected}  x={decode(selected)}  f={fitness(selected)}")

    print("\nCrossover test: [0,1,1,0] x [1,0,0,1] at point 2")
    o1, o2 = single_point_crossover([0,1,1,0], [1,0,0,1], 2)
    print(f"  Offspring 1: {o1}  x={decode(o1)}  f={fitness(o1)}")
    print(f"  Offspring 2: {o2}  x={decode(o2)}  f={fitness(o2)}")

    print("\nMutation test: [1,1,0,0] with p_m=0.1, seed=42")
    random.seed(42)
    m = mutate([1,1,0,0], 0.1)
    print(f"  Original:  [1, 1, 0, 0]  x=12  f=29")
    print(f"  Mutated:   {m}  x={decode(m)}  f={fitness(m)}")


# ── part (b) ───

def run_ga(pop_size, num_generations, p_m, elitism):
    population = [[random.randint(0,1) for _ in range(4)]
                  for _ in range(pop_size)]
    history = []

    for gen in range(1, num_generations + 1):
        fits = [fitness(c) for c in population]
        best_idx = fits.index(max(fits))
        best_fit = fits[best_idx]
        best_x = decode(population[best_idx])
        history.append((gen, best_fit, best_x))

        print(f"\nGeneration {gen}:")
        print(f"  {'#':<4} {'Chromosome':<20} {'x':>4} {'f(x)':>6}")
        print(f"  {'-'*38}")
        for i, (c, f) in enumerate(zip(population, fits)):
            marker = " <-- best" if i == best_idx else ""
            print(f"  {i+1:<4} {str(c):<20} {decode(c):>4} {f:>6}{marker}")
        print(f"  Best this gen: x={best_x}, f={best_fit}")

        new_pop = []
        if elitism:
            new_pop.append(population[best_idx][:])

        while len(new_pop) < pop_size:
            p1 = roulette_select(population)
            p2 = roulette_select(population)
            point = random.randint(1, 3)
            o1, o2 = single_point_crossover(p1, p2, point)
            o1 = mutate(o1, p_m)
            o2 = mutate(o2, p_m)
            new_pop.append(o1)
            if len(new_pop) < pop_size:
                new_pop.append(o2)

        population = new_pop

    return history


# ── part (c) ──

def run_ga_silent(pop_size, num_generations, p_m, elitism):
    population = [[random.randint(0,1) for _ in range(4)]
                  for _ in range(pop_size)]
    history = []
    for gen in range(1, num_generations + 1):
        fits = [fitness(c) for c in population]
        best_idx = fits.index(max(fits))
        best_fit = fits[best_idx]
        best_x = decode(population[best_idx])
        history.append((gen, best_fit, best_x))
        new_pop = []
        if elitism:
            new_pop.append(population[best_idx][:])
        while len(new_pop) < pop_size:
            p1 = roulette_select(population)
            p2 = roulette_select(population)
            point = random.randint(1, 3)
            o1, o2 = single_point_crossover(p1, p2, point)
            o1 = mutate(o1, p_m)
            o2 = mutate(o2, p_m)
            new_pop.append(o1)
            if len(new_pop) < pop_size:
                new_pop.append(o2)
        population = new_pop
    return history


def experiment_elitism(trials=30):
    results = {}
    for elitism in [False, True]:
        found_optimum = 0
        total_best = []
        gen_to_50 = []
        for _ in range(trials):
            h = run_ga_silent(4, 20, 0.1, elitism)
            best = max(bf for _, bf, _ in h)
            total_best.append(best)
            if any(bx == 7 for _, _, bx in h):
                found_optimum += 1
            for gen, bf, _ in h:
                if bf >= 50:
                    gen_to_50.append(gen)
                    break
        avg_best = sum(total_best) / trials
        avg_gen = (sum(gen_to_50) / len(gen_to_50)
                   if gen_to_50 else float('nan'))
        results[elitism] = (avg_best, found_optimum, avg_gen)
    return results


def experiment_mutation(trials=30):
    rates = [0.01, 0.1, 0.3, 0.5]
    results = {}
    for pm in rates:
        bests = []
        for _ in range(trials):
            h = run_ga_silent(4, 20, pm, False)
            bests.append(max(bf for _, bf, _ in h))
        results[pm] = sum(bests) / trials
    return results




if __name__ == "__main__":

    run_part_a()

    print("\nRunning Part (b): pop=4, gen=10, pm=0.1, elitism=False")
    random.seed(7)
    history = run_ga(4, 10, 0.1, False)

    print("\nSummary Table:")
    print(f"{'Gen':>4} {'Best x':>7} {'Best f(x)':>10}")
    print("-" * 24)
    for gen, bf, bx in history:
        print(f"{gen:>4} {bx:>7} {bf:>10}")

    print("\nRunning Part (c): elitism experiment")
    random.seed(99)
    el_results = experiment_elitism(30)
    print(f"{'Setting':<20} {'Avg Best f':>12} {'Found x=7':>11} {'Avg Gen to f>=50':>18}")
    print("-" * 63)
    for elitism, (avg_best, found_opt, avg_gen) in el_results.items():
        label = "Elitism=True" if elitism else "Elitism=False"
        ag = f"{avg_gen:.2f}" if not math.isnan(avg_gen) else "N/A"
        print(f"{label:<20} {avg_best:>12.2f} {found_opt:>11} {ag:>18}")

    print("\nRunning Part (c): mutation rate experiment")
    random.seed(99)
    mut_results = experiment_mutation(30)
    print(f"{'p_m':<8} {'Avg Best f(x)':>14}")
    print("-" * 24)
    for pm, avg in mut_results.items():
        print(f"{pm:<8} {avg:>14.2f}")