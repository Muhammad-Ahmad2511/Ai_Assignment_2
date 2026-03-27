import random

# warehouse shelf positions - score = utility based on proximity to packing station
# shelf_scores[i] = f(i+1), positions 1 to 14
shelf_scores = [5, 8, 6, 12, 9, 7, 17, 14, 10, 6, 19, 15, 11, 8]


def first_choice_hc(shelf_scores, start, sideways_limit=0):
    current = start
    path = [current]
    sideways = 0

    while True:
        idx = current - 1
        curr_val = shelf_scores[idx]
        moved = False

        # check left neighbour first
        if current > 1:
            left = shelf_scores[idx - 1]
            if left > curr_val:
                current -= 1
                path.append(current)
                moved = True
                continue
            elif left == curr_val:
                if sideways < sideways_limit:
                    current -= 1
                    path.append(current)
                    sideways += 1
                    moved = True
                    continue
                else:
                    break

        # check right neighbour
        if not moved and current < len(shelf_scores):
            right = shelf_scores[idx + 1]
            if right > curr_val:
                current += 1
                path.append(current)
                moved = True
                continue
            elif right == curr_val:
                if sideways < sideways_limit:
                    current += 1
                    path.append(current)
                    sideways += 1
                    moved = True
                    continue
                else:
                    break

        if not moved:
            break

    return path, current


def stochastic_hc(shelf_scores, start, sideways_limit=0):
    current = start
    path = [current]
    sideways = 0

    while True:
        idx = current - 1
        curr_val = shelf_scores[idx]
        uphill = []
        equal = []

        if current > 1:
            if shelf_scores[idx - 1] > curr_val:
                uphill.append(current - 1)
            elif shelf_scores[idx - 1] == curr_val:
                equal.append(current - 1)

        if current < len(shelf_scores):
            if shelf_scores[idx + 1] > curr_val:
                uphill.append(current + 1)
            elif shelf_scores[idx + 1] == curr_val:
                equal.append(current + 1)

        if uphill:
            current = random.choice(uphill)
            path.append(current)
        elif equal:
            if sideways < sideways_limit:
                current = random.choice(equal)
                path.append(current)
                sideways += 1
            else:
                break
        else:
            break

    return path, current


def find_local_maxima(shelf_scores):
    # returns positions (1-indexed) where score beats both neighbours
    # boundary positions excluded since they have only one neighbour
    peaks = []
    for i in range(1, len(shelf_scores) - 1):
        if shelf_scores[i] > shelf_scores[i - 1] and shelf_scores[i] > shelf_scores[i + 1]:
            peaks.append(i + 1)
    return peaks


def random_restart_hc(shelf_scores, num_restarts, variant='first_choice',
                       plateau_states=None):
    best_pos = None
    best_score = -1
    all_results = []
    plateau_count = 0

    for _ in range(num_restarts):
        # pick random start position uniformly
        start = random.randint(0, len(shelf_scores) - 1) + 1

        if variant == 'first_choice':
            path, terminal = first_choice_hc(shelf_scores, start)
        else:
            path, terminal = stochastic_hc(shelf_scores, start)

        score = shelf_scores[terminal - 1]
        all_results.append((start, terminal, path))

        # count restarts that got stuck on plateau
        if plateau_states and terminal in plateau_states:
            plateau_count += 1

        if score > best_score:
            best_score = score
            best_pos = terminal

    return best_pos, best_score, all_results, plateau_count


def main():
    # part (a) - local maxima
    peaks = find_local_maxima(shelf_scores)
    print(f"Local maxima positions: {peaks}")
    print(f"Global maximum: position 11, score=19")

    # part (a) - RRHC 20 restarts, both variants
    for variant in ['first_choice', 'stochastic']:
        print(f"\nRRHC  variant={variant}  restarts=20")
        print(f"{'Restart':<10}{'Start':<8}{'Terminal':<12}{'Score':<10}{'Global max?'}")
        print("-" * 50)
        best_p, best_s, results, _ = random_restart_hc(shelf_scores, 20, variant)
        for i, (start, terminal, path) in enumerate(results):
            sc = shelf_scores[terminal - 1]
            gmax = 'yes' if terminal == 11 else 'no'
            print(f"{i+1:<10}{start:<8}{terminal:<12}{sc:<10}{gmax}")
        print(f"\nBest position: {best_p},  best score: {best_s}")

    # part (b) - find p from Q2 landscape under first choice HC
    reach_global = 0
    for s in range(1, len(shelf_scores) + 1):
        _, t = first_choice_hc(shelf_scores, s)
        if t == 11:
            reach_global += 1
    p = reach_global / len(shelf_scores)
    print(f"\np = {reach_global}/{len(shelf_scores)} = {p:.4f}")

    # part (b) - empirical vs theoretical probability
    print(f"\n{'n':<6}{'Empirical P':<16}{'Theoretical P'}")
    print("-" * 36)
    for n in [1, 3, 5, 10, 20]:
        success = 0
        for _ in range(100):
            bp, _, _, _ = random_restart_hc(shelf_scores, n, 'first_choice')
            if bp == 11:
                success += 1
        emp = success / 100
        theo = 1 - (1 - p) ** n
        print(f"{n:<6}{emp:<16.2f}{theo:.4f}")

    # part (c) - plateau: positions 7 and 8 both set to score 17
    shelf_scores_plateau = [5, 8, 6, 12, 9, 7, 17, 17, 10, 6, 19, 15, 11, 8]
    plateau_pos = {7, 8}

    print("\nBefore plateau modification, restarts=20:")
    print(f"{'Restart':<10}{'Start':<8}{'Terminal':<12}{'Score':<10}{'Global max?'}")
    print("-" * 50)
    orig_found = 0
    _, _, results, p_count = random_restart_hc(
        shelf_scores, 20, 'first_choice', plateau_states={7})
    for i, (start, terminal, path) in enumerate(results):
        sc = shelf_scores[terminal - 1]
        gmax = 'yes' if terminal == 11 else 'no'
        if terminal == 11:
            orig_found += 1
        print(f"{i+1:<10}{start:<8}{terminal:<12}{sc:<10}{gmax}")
    print(f"\nGlobal max found: {orig_found}/20")
    print(f"Stuck at position 7: {p_count}/20")

    print("\nAfter plateau modification (positions 7,8 both score=17), restarts=20:")
    print(f"{'Restart':<10}{'Start':<8}{'Terminal':<12}{'Score':<10}{'Global max?'}")
    print("-" * 50)
    plat_found = 0
    _, _, results, p_count = random_restart_hc(
        shelf_scores_plateau, 20, 'first_choice', plateau_states=plateau_pos)
    for i, (start, terminal, path) in enumerate(results):
        sc = shelf_scores_plateau[terminal - 1]
        gmax = 'yes' if terminal == 11 else 'no'
        if terminal == 11:
            plat_found += 1
        print(f"{i+1:<10}{start:<8}{terminal:<12}{sc:<10}{gmax}")
    print(f"\nGlobal max found: {plat_found}/20")
    print(f"Stuck at plateau (positions 7 or 8): {p_count}/20")

    print("\nComparison:")
    print(f"{'Landscape':<28}{'Global max':<18}{'Plateau stuck'}")
    print("-" * 55)
    print(f"{'Original':<28}{str(orig_found)+'/20':<18}{'N/A'}")
    print(f"{'Plateau (7,8=17)':<28}{str(plat_found)+'/20':<18}{str(p_count)+'/20'}")


main()