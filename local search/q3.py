import random
import math

# PART (a): Diagnosing Hill Climbing Failures

def get_value(landscape, state):
    return landscape[state]["value"]


def get_neighbours(landscape, state):
    return landscape[state]["neighbours"]


def diagnose_hc(landscape, start):
    current        = start
    visited        = [current]
    visited_set    = {current}
    sideways_steps = 0
    max_steps      = 10_000

    for _ in range(max_steps):
        current_val = get_value(landscape, current)
        neighbours  = get_neighbours(landscape, current)[:]
        random.shuffle(neighbours)

        better = [n for n in neighbours if get_value(landscape, n) > current_val]
        equal  = [n for n in neighbours if get_value(landscape, n) == current_val]

        if better:
            move_to = better[0]
            if move_to in visited_set:
                # Strictly-better move leads back to a visited state — Ridge
                print(f"Terminated at state {current} with f={current_val}. "
                      f"Failure mode: Ridge")
                return current, "Ridge"
            current = move_to
            visited.append(current)
            visited_set.add(current)

        elif equal:
            looping   = [n for n in equal if n in visited_set]
            unvisited = [n for n in equal if n not in visited_set]

            if looping:
                # Equal step would revisit — Ridge (oscillation)
                print(f"Terminated at state {current} with f={current_val}. "
                      f"Failure mode: Ridge")
                return current, "Ridge"
            else:
                # Step sideways into unvisited equal territory
                move_to = unvisited[0]
                current = move_to
                visited.append(current)
                visited_set.add(current)
                sideways_steps += 1

        else:
            # No better, no equal neighbours
            if sideways_steps > 0:
                # Exhausted a flat region — Plateau
                print(f"Terminated at state {current} with f={current_val}. "
                      f"Failure mode: Plateau")
                return current, "Plateau"
            else:
                # Pure climbing peak — Local Maximum
                print(f"Terminated at state {current} with f={current_val}. "
                      f"Failure mode: Local Maximum")
                return current, "Local Maximum"

    current_val = get_value(landscape, current)
    print(f"Terminated at state {current} with f={current_val}. "
          f"Failure mode: Ridge (step cap reached)")
    return current, "Ridge"

def build_local_max_landscape():

    return {
        "A": {"value": 1, "neighbours": ["B"]},
        "B": {"value": 3, "neighbours": ["A", "C"]},
        "C": {"value": 5, "neighbours": ["B", "D", "E"]},
        "D": {"value": 4, "neighbours": ["C"]},
        "E": {"value": 2, "neighbours": ["C"]},
    }


def build_plateau_landscape():
   return {
        "A": {"value": 1, "neighbours": ["B"]},
        "B": {"value": 3, "neighbours": ["A", "C"]},
        "C": {"value": 6, "neighbours": ["B", "D"]},
        "D": {"value": 9, "neighbours": ["C", "E"]},
        "E": {"value": 9, "neighbours": ["F"]},         # forward-only, no back to D
        "F": {"value": 9, "neighbours": ["G"]},         # forward-only, no back to E
        "G": {"value": 2, "neighbours": ["F"]},         # worse dead-end
    }


def build_ridge_landscape():      
    return {
        "start": {"value": 1, "neighbours": ["A"]},
        "A":     {"value": 4, "neighbours": ["start", "B"]},
        "B":     {"value": 7, "neighbours": ["A", "C"]},
        "C":     {"value": 7, "neighbours": ["B", "D"]},
        "D":     {"value": 2, "neighbours": ["C"]},
    }


def run_part_a():
    print("=" * 60)
    print("PART (a): Diagnosing HC Failure Modes")
    print("=" * 60)

    random.seed(42)

    print("\n--- Landscape 1: Expected --> Local Maximum ---")
    diagnose_hc(build_local_max_landscape(), "A")

    print("\n--- Landscape 2: Expected --> Plateau ---")
    diagnose_hc(build_plateau_landscape(), "A")

    print("\n--- Landscape 3: Expected --> Ridge ---")
    diagnose_hc(build_ridge_landscape(), "start")

# PART (b): N-Queens with Stochastic HC + Random Restarts


def count_conflicts(board):
    n = len(board)
    conflicts = 0
    for i in range(n):
        for j in range(i + 1, n):
            if board[i] == board[j]:
                conflicts += 1
            elif abs(board[i] - board[j]) == abs(i - j):
                conflicts += 1
    return conflicts


def stochastic_hc_nqueens(board, max_iterations=2000):
    n = len(board)
    current           = board[:]
    current_conflicts = count_conflicts(current)

    for _ in range(max_iterations):
        if current_conflicts == 0:
            break
        i, j      = random.sample(range(n), 2)
        candidate = current[:]
        candidate[i], candidate[j] = candidate[j], candidate[i]
        cand_conf = count_conflicts(candidate)
        if cand_conf < current_conflicts:
            current           = candidate
            current_conflicts = cand_conf

    return current, current_conflicts


def solve_nqueens_rrhc(num_restarts, n=8):
    best_board     = None
    best_conflicts = math.inf

    for restart in range(1, num_restarts + 1):
        start = list(range(n))
        random.shuffle(start)
        result, conf = stochastic_hc_nqueens(start)

        if conf < best_conflicts:
            best_conflicts = conf
            best_board     = result[:]

        if conf == 0:
            return result, restart

    return best_board, num_restarts


def print_board(board):
    n = len(board)
    print("  " + " ".join(str(c) for c in range(n)))
    for row in range(n):
        line = ["Q" if board[col] == row else "." for col in range(n)]
        print(f"{row} " + " ".join(line))


def run_part_b():
    print("\n" + "=" * 60)
    print("PART (b): N-Queens — Stochastic HC + Random Restarts")
    print("=" * 60)

    random.seed(0)
    solution, restarts_used = solve_nqueens_rrhc(100, n=8)
    conflicts = count_conflicts(solution)

    print(f"\nsolve_nqueens_rrhc(100):")
    print(f"  Restarts needed  : {restarts_used}")
    print(f"  Conflicts        : {conflicts}")
    print(f"  Solution found   : {'YES' if conflicts == 0 else 'NO — best board shown'}")
    print(f"  Board (col->row) : {solution}")
    print("\nBoard visualisation (row 0 = top):")
    print_board(solution)

# PART (c): Benchmarking

def benchmark_nqueens(k_values, trials=30, n=8):
   
    results = {}
    for k in k_values:
        successes      = 0
        restart_counts = []
        for _ in range(trials):
            board, restarts = solve_nqueens_rrhc(k, n=n)
            if count_conflicts(board) == 0:
                successes += 1
                restart_counts.append(restarts)
        results[k] = {
            "success_rate": successes / trials,
            "avg_restarts": (sum(restart_counts) / len(restart_counts)
                             if restart_counts else float("nan")),
        }
    return results

def run_part_c():
    print("\n" + "=" * 60)
    print("PART (c): Benchmark Results")
    print("=" * 60)

    random.seed(123)
    k_values = [5, 10, 25, 50, 100]
    results  = benchmark_nqueens(k_values, trials=30)

    print(f"\n{'k':>6}  {'Success Rate':>14}  {'Avg Restarts to Solution':>26}")
    print("-" * 52)
    for k in k_values:
        r  = results[k]
        sr = f"{r['success_rate']:.2%}"
        ar = f"{r['avg_restarts']:.2f}" if not math.isnan(r['avg_restarts']) else "N/A"
        print(f"{k:>6}  {sr:>14}  {ar:>26}")

if __name__ == "__main__":
    run_part_a()
    run_part_b()
    run_part_c()