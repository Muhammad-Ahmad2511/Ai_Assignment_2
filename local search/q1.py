import random

landscape = [4, 9, 6, 11, 8, 15, 10, 7, 13, 5, 16, 12]


def first_choice_hc(landscape, start):
    """
    First-Choice Hill Climbing.
      - Always checks the LEFT neighbour before the right.
      - Moves immediately on the FIRST improvement found.
    Returns: (path, terminal_state)
    """
    current = start
    path    = [current]

    while True:
        idx         = current - 1        # convert state number to list index
        current_val = landscape[idx]
        moved       = False

        # --- check LEFT neighbour first ---
        if current > 1:
            if landscape[idx - 1] > current_val:
                current -= 1
                path.append(current)
                moved = True
                continue                  # first improvement found → move immediately

        # check RIGHT neighbour only if left gave no improvement 
        if not moved and current < len(landscape):
            if landscape[idx + 1] > current_val:
                current += 1
                path.append(current)
                moved = True
                continue

        # --- no improvement on either side → local maximum, terminate ---
        if not moved:
            break

    return path, current


def stochastic_hc(landscape, start):
    """
    Stochastic Hill Climbing.
      - Collects ALL strictly uphill neighbours first.
      - Picks one at random using random.choice().
    Returns: (path, terminal_state)
    """
    current = start
    path    = [current]

    while True:
        idx         = current - 1
        current_val = landscape[idx]
        uphill      = []

        # gather left neighbour if strictly uphill
        if current > 1:
            if landscape[idx - 1] > current_val:
                uphill.append(current - 1)

        # gather right neighbour if strictly uphill
        if current < len(landscape):
            if landscape[idx + 1] > current_val:
                uphill.append(current + 1)

        if uphill:
            current = random.choice(uphill)   # pick randomly among uphill neighbours
            path.append(current)
        else:
            break                             # no uphill neighbour → local maximum

    return path, current

def main():

   
    print("=" * 68)
    print("  PART (a) — Both algorithms from all 12 starting states")
    print("  Landscape : f = [4, 9, 6, 11, 8, 15, 10, 7, 13, 5, 16, 12]")
    print("  Global max: state 11  (f = 16)")
    print("=" * 68)
    print()
    print(f"  {'Start':>5}  {'Algorithm':<14}  {'Path':<34}  {'Terminal':>8}  {'Steps':>5}")
    print("  " + "-" * 67)

    # store results to reuse in divergence analysis
    results   = {}
    fc_global = 0
    st_global = 0

    for start in range(1, 13):
        p1, t1 = first_choice_hc(landscape, start)
        p2, t2 = stochastic_hc(landscape, start)
        results[start] = (p1, t1, p2, t2)      # store here, reuse below

        if t1 == 11:
            fc_global += 1
        if t2 == 11:
            st_global += 1

        print(f"  {start:>5}  {'First-Choice':<14}  {str(p1):<34}  {t1:>8}  {len(p1)-1:>5}")
        print(f"  {start:>5}  {'Stochastic':<14}  {str(p2):<34}  {t2:>8}  {len(p2)-1:>5}")

    #  Summary: how many reach global max 
    print()
    print("  ── Summary: how many starting states reach global max (state 11)? ──")
    print()
    print(f"  {'Algorithm':<14}  {'Reaches state 11':>17}  {'Does NOT reach':>14}")
    print("  " + "-" * 48)
    print(f"  {'First-Choice':<14}  {str(fc_global) + ' / 12':>17}  {str(12 - fc_global) + ' / 12':>14}")
    print(f"  {'Stochastic':<14}  {str(st_global) + ' / 12':>17}  {str(12 - st_global) + ' / 12':>14}")
    print()
    print("  Note: Stochastic HC is random — its count may vary per run.")

    # ── Divergence analysis ──
    print()
    print("  ── PART (b) — Starting states where both algorithms diverge ──")
    print()

    any_diverged = False
    for start in range(1, 13):
        p1, t1, p2, t2 = results[start]        # reuse stored results, no re-calling
        if t1 != t2:
            any_diverged = True
            print(f"  Start = {start}  (f({start}) = {landscape[start-1]})")
            print(f"    First-Choice → path {p1}  →  terminal {t1}  (f={landscape[t1-1]})")
            print(f"    Stochastic   → path {p2}  →  terminal {t2}  (f={landscape[t2-1]})")
            if start > 1 and start < 12:
                lv = landscape[start - 2]
                rv = landscape[start]
                print(f"    Neighbours: left = state {start-1} f={lv},  "
                      f"right = state {start+1} f={rv}")
            print(f"    First-Choice commits to the LEFT neighbour on first improvement,")
            print(f"    so it can get trapped at a closer local peak.")
            print(f"    Stochastic collects BOTH uphill neighbours and picks randomly,")
            print(f"    so it may choose the other direction and reach a better state.")
            print()

    if not any_diverged:
        print("  No divergence this run. Re-run to observe stochastic differences.")

    #  50-trial experiment from state 4 
    print()
    print("  50-trial experiment: Stochastic HC from s = 4 ")
    print()
    print("  Landscape check at state 4:")
    print(f"    f(3) = {landscape[2]}  (left neighbour)  — downhill from f(4)={landscape[3]}")
    print(f"    f(4) = {landscape[3]}  (start state)")
    print(f"    f(5) = {landscape[4]}  (right neighbour) — downhill from f(4)={landscape[3]}")
    print()
    print("  State 4 is a LOCAL MAXIMUM — both neighbours are strictly lower.")
    print("  Stochastic HC will find zero uphill neighbours and stop immediately.")
    print()

    reach_11 = 0
    for _ in range(50):
        _, t = stochastic_hc(landscape, 4)
        if t == 11:
            reach_11 += 1

    stuck = 50 - reach_11
    print(f"  Result of 50 trials:")
    print(f"    Reached global max (state 11) : {reach_11} / 50  ({reach_11 / 50 * 100:.1f}%)")
    print(f"    Stuck at local max  (state 4) : {stuck} / 50  ({stuck / 50 * 100:.1f}%)")
    print()
    
    """Interpretation: Stochastic HC terminates in 0 steps every trial"
      because state 4 has no uphill neighbours. This shows that stochastic"
      selection among neighbours is useless when no uphill neighbour exists."
      The algorithm's reliability is entirely determined by the landscape"
      topology at the starting state — random restarts are the only remedy."""


main()

landscape_plateau = [4, 9, 6, 11, 15, 15, 15, 7, 13, 5, 16, 12]


def first_choice_hc_plateau(landscape, start, sideways_limit=0):
    """
    First-Choice HC with plateau detection and sideways-move extension.
      - Prints a warning whenever it detects a plateau (equal neighbour).
      - Allows up to sideways_limit equal-value moves per run.
    Returns: (path, terminal_state)
    """
    current  = start
    path     = [current]
    sideways = 0

    while True:
        idx         = current - 1
        current_val = landscape[idx]
        moved       = False

        # --- LEFT neighbour ---
        if current > 1:
            left_val = landscape[idx - 1]

            if left_val > current_val:
                current -= 1
                path.append(current)
                moved = True
                continue

            elif left_val == current_val:
                if sideways < sideways_limit:
                    print(f"  [PLATEAU] State {current} (f={current_val}): "
                          f"left neighbour state {current-1} is equal. "
                          f"Sideways move {sideways+1}/{sideways_limit}.")
                    current -= 1
                    path.append(current)
                    sideways += 1
                    moved = True
                    continue
                else:
                    print(f"  [PLATEAU] State {current} (f={current_val}): "
                          f"left neighbour equal but sideways cap ({sideways_limit}) reached.")
                    break

        # --- RIGHT neighbour ---
        if not moved and current < len(landscape):
            right_val = landscape[idx + 1]

            if right_val > current_val:
                current += 1
                path.append(current)
                moved = True
                continue

            elif right_val == current_val:
                if sideways < sideways_limit:
                    print(f"  [PLATEAU] State {current} (f={current_val}): "
                          f"right neighbour state {current+1} is equal. "
                          f"Sideways move {sideways+1}/{sideways_limit}.")
                    current += 1
                    path.append(current)
                    sideways += 1
                    moved = True
                    continue
                else:
                    print(f"  [PLATEAU] State {current} (f={current_val}): "
                          f"right neighbour equal but sideways cap ({sideways_limit}) reached.")
                    break

        if not moved:
            break

    return path, current


def stochastic_hc_plateau(landscape, start, sideways_limit=0):
    """
    Stochastic HC with plateau detection and sideways-move extension.
      - Collects ALL strictly uphill neighbours; picks randomly.
      - If no uphill but equal neighbours exist → plateau warning.
      - Allows up to sideways_limit equal-value moves per run.
    Returns: (path, terminal_state)
    """
    current  = start
    path     = [current]
    sideways = 0

    while True:
        idx         = current - 1
        current_val = landscape[idx]
        uphill = []
        equal  = []

        if current > 1:
            left_val = landscape[idx - 1]
            if left_val > current_val:
                uphill.append(current - 1)
            elif left_val == current_val:
                equal.append(current - 1)

        if current < len(landscape):
            right_val = landscape[idx + 1]
            if right_val > current_val:
                uphill.append(current + 1)
            elif right_val == current_val:
                equal.append(current + 1)

        if uphill:
            current = random.choice(uphill)
            path.append(current)

        elif equal:
            if sideways < sideways_limit:
                print(f"  [PLATEAU] State {current} (f={current_val}): "
                      f"equal neighbours {equal}, no uphill found. "
                      f"Sideways move {sideways+1}/{sideways_limit}.")
                current = random.choice(equal)
                path.append(current)
                sideways += 1
            else:
                print(f"  [PLATEAU] State {current} (f={current_val}): "
                      f"equal neighbours {equal} but sideways cap ({sideways_limit}) reached.")
                break

        else:
            break

    return path, current


def main_partc():

    print()
    print("=" * 68)
    print("  PART (c) — Plateau Landscape")
    print("  f = [4, 9, 6, 11, 15, 15, 15, 7, 13, 5, 16, 12]")
    print("  States 5, 6, 7 all have f = 15  →  flat plateau")
    print("  Global max: state 11  (f = 16)")
    print("=" * 68)

   
    #  WITHOUT sideways moves (cap = 0)
  
    print()
    print("  Run WITHOUT sideways moves (cap = 0) ")
    print()
    print(f"  {'Start':>5}  {'Algorithm':<14}  {'Terminal':>8}  {'f(terminal)':>12}  {'Global max?':>11}")
    print("  " + "-" * 55)

    fc_stuck = 0
    st_stuck = 0

    for start in range(1, 13):
        p1, t1 = first_choice_hc_plateau(landscape_plateau, start, sideways_limit=0)
        p2, t2 = stochastic_hc_plateau(landscape_plateau, start, sideways_limit=0)

        if t1 != 11:
            fc_stuck += 1
        if t2 != 11:
            st_stuck += 1

        print(f"  {start:>5}  {'First-Choice':<14}  {t1:>8}  "
              f"{landscape_plateau[t1-1]:>12}  {'YES' if t1==11 else 'no':>11}")
        print(f"  {start:>5}  {'Stochastic':<14}  {t2:>8}  "
              f"{landscape_plateau[t2-1]:>12}  {'YES' if t2==11 else 'no':>11}")

    print()
    print(f"  Runs that did NOT reach global max:")
    print(f"    First-Choice : {fc_stuck} / 12  stuck on plateau or local max")
    print(f"    Stochastic   : {st_stuck} / 12  stuck on plateau or local max")

    
    #  WITH sideways moves (cap = 10)
   
    print()
    print("  ── Run WITH sideways moves (cap = 10) ──")
    print()
    print(f"  {'Start':>5}  {'Algorithm':<14}  {'Terminal':>8}  {'f(terminal)':>12}  {'Global max?':>11}")
    print("  " + "-" * 55)

    fc_success = 0
    st_success = 0

    for start in range(1, 13):
        p1, t1 = first_choice_hc_plateau(landscape_plateau, start, sideways_limit=10)
        p2, t2 = stochastic_hc_plateau(landscape_plateau, start, sideways_limit=10)

        if t1 == 11:
            fc_success += 1
        if t2 == 11:
            st_success += 1

        print(f"  {start:>5}  {'First-Choice':<14}  {t1:>8}  "
              f"{landscape_plateau[t1-1]:>12}  {'YES' if t1==11 else 'no':>11}")
        print(f"  {start:>5}  {'Stochastic':<14}  {t2:>8}  "
              f"{landscape_plateau[t2-1]:>12}  {'YES' if t2==11 else 'no':>11}")

    print()
    print(f"  Runs that DID reach global max:")
    print(f"    First-Choice : {fc_success} / 12")
    print(f"    Stochastic   : {st_success} / 12")


    #  Before vs After comparison table
    
    print()
    print("  ── Before vs After — sideways move effect ──")
    print()
    print(f"  {'Algorithm':<14}  {'Without sideways':>16}  {'With sideways(cap=10)':>21}")
    print("  " + "-" * 54)
    print(f"  {'First-Choice':<14}  {str(12-fc_stuck)+' / 12':>16}  {str(fc_success)+' / 12':>21}")
    print(f"  {'Stochastic':<14}  {str(12-st_stuck)+' / 12':>16}  {str(st_success)+' / 12':>21}")


"""
In this run, sideways moves didn't improve First-Choice or Stochastic HC, as both reached the global maximum at the same rates (2/12 and 3/12) 
The plateau (states 5–7, f=15) lacks uphill exits, meaning traversing it leads only to lower values at states 4 and 8, offering no escape route. 
First-Choice oscillates between 5 and 6, while Stochastic explores the plateau randomly, yet neither can find a path to a higher peak from 
this region The 10-move cap is critical here; without it, both algorithms would loop indefinitely on the flat 
plateau, making the cap the only termination guarantee
"""

main_partc()