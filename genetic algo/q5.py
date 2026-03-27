import random
import math
from collections import defaultdict

courses = 6
rooms   = 3   # indices 0,1,2 → R1,R2,R3
slots   = 4   # indices 0,1,2,3 → T1,T2,T3,T4

def random_chromosome():
    """Return a list of 6 (room_idx, slot_idx) tuples."""
    return [(random.randint(0, rooms-1), random.randint(0, slots-1))
            for _ in range(courses)]

def count_conflicts(chromosome):
    """Count pairs of courses sharing the same (room, slot)."""
    seen = defaultdict(list)
    for i, gene in enumerate(chromosome):
        seen[gene].append(i)
    conflicts = 0
    for courses in seen.values():
        n = len(courses)
        conflicts += n * (n - 1) // 2   # C(n,2) pairs
    return conflicts

def fitness(chromosome):
    return 100 - 10 * count_conflicts(chromosome)

# Print 5 random chromosomes
header = f"{'Chr':>3}  {'Chromosome':<50}  {'Conflicts':>9}  {'Fitness':>7}"
print(header)
print("-" * 72)
for i in range(5):
    ch = random_chromosome()
    c  = count_conflicts(ch)
    f  = fitness(ch)
    print(f"{i+1:>3}  {str(ch):<50}  {c:>9}  {f:>7}")



##  part (b)  ##

def crossover(p1, p2, point):
    """Single-point crossover at position 'point'."""
    child1 = p1[:point] + p2[point:]
    child2 = p2[:point] + p1[point:]
    return child1, child2

def repair(chromosome):
    """Detect conflicted courses and reassign to a conflict-free (room,slot)."""
    assignment = defaultdict(list)
    for i, gene in enumerate(chromosome):
        assignment[gene].append(i)

    repaired = list(chromosome)
    for gene, courses in assignment.items():
        if len(courses) > 1:
            # Keep first course, repair the rest
            for ci in courses[1:]:
                occupied = set(repaired)
                free = [(r, s) for r in range(rooms)
                                for s in range(slots)
                                if (r, s) not in occupied]
                if free:
                    repaired[ci] = random.choice(free)
                else:
                    repaired[ci] = (random.randint(0, rooms-1),
                                    random.randint(0, slots-1))
    return repaired

def mutate(chromosome, p_m):
    """With probability p_m per gene, reassign that course randomly."""
    return [(random.randint(0, rooms-1), random.randint(0, slots-1))
            if random.random() < p_m else gene
            for gene in chromosome]

# Crossover demo
p1 = [(0,0),(1,1),(2,2),(0,3),(1,0),(2,1)]
p2 = [(0,1),(1,2),(2,3),(0,0),(1,1),(2,2)]
child1, child2 = crossover(p1, p2, point=3)
print(f"Parent 1 : {p1}  conflicts={count_conflicts(p1)}")
print(f"Parent 2 : {p2}  conflicts={count_conflicts(p2)}")
print(f"Child 1  : {child1}  conflicts={count_conflicts(child1)}")
print(f"Child 2  : {child2}  conflicts={count_conflicts(child2)}")
print("→ Crossover introduced a conflict (expected behaviour).")

# Repair demo
conflicted = [(0,0),(0,0),(1,1),(1,1),(2,2),(2,0)]
repaired   = repair(conflicted)
print(f"Before repair : {conflicted}  conflicts={count_conflicts(conflicted)}")
print(f"After  repair : {repaired}   conflicts={count_conflicts(repaired)}")



## part (c) ##

def tournament_select(population, fits, k=2):
    """Randomly pick k individuals; return the fitter one."""
    indices = random.sample(range(len(population)), k)
    best    = max(indices, key=lambda i: fits[i])
    return population[best]

def run_scheduling_ga(pop_size=20, generations=50, p_m=0.1):
    population = [random_chromosome() for _ in range(pop_size)]
    fits       = [fitness(c) for c in population]
    best_per_gen = []
    solution_gen = None
    solution_chr = None

    for gen in range(generations):
        new_pop = []
        while len(new_pop) < pop_size:
            p1    = tournament_select(population, fits)
            p2    = tournament_select(population, fits)
            point = random.randint(1, courses - 1)
            c1, c2 = crossover(p1, p2, point)
            c1 = repair(c1);   c2 = repair(c2)    # repair after crossover
            c1 = mutate(c1, p_m); c2 = mutate(c2, p_m)
            new_pop.extend([c1, c2])

        population   = new_pop[:pop_size]
        fits         = [fitness(c) for c in population]
        best_idx     = max(range(pop_size), key=lambda i: fits[i])
        best_per_gen.append(fits[best_idx])

        if fits[best_idx] == 100 and solution_gen is None:
            solution_gen = gen + 1
            solution_chr = population[best_idx]

    best_idx = max(range(pop_size), key=lambda i: fits[i])
    return population[best_idx], fits[best_idx], best_per_gen, solution_gen, solution_chr

random.seed(42)
best_chr, best_fit, history, sol_gen, sol_chr = run_scheduling_ga(
    pop_size=20, generations=50, p_m=0.1
)

rooms_label = {0:'R1', 1:'R2', 2:'R3'}
slots_label = {0:'T1', 1:'T2', 2:'T3', 3:'T4'}
print(f"{'Course':<8} {'Room':<6} {'Slot'}")
print("-" * 24)
for i, (r, s) in enumerate(best_chr):
    print(f"C{i+1:<7} {rooms_label[r]:<6} {slots_label[s]}")
print(f"\nConflicts : {count_conflicts(best_chr)}")
print(f"Fitness   : {best_fit}")

if sol_gen:
    print(f"\nSolution found at generation {sol_gen}: {sol_chr}")

