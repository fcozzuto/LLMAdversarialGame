def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    srole = str(observation.get("self_role", "")).lower()
    is_pursuer = ("purs" in srole) or ("chase" in srole) or ("seeker" in srole)

    obstacles = observation.get("obstacles", []) or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in oset

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic tie-break preference toward diagonals, then toward decreasing/increasing manhattan.
    diag_pref = {(dx, dy): 1 if (dx != 0 and dy != 0) else 0 for dx, dy in moves}

    def min_dist_to_obstacles(x, y):
        if not oset:
            return 999
        md = 999
        for (px, py) in oset:
            d = abs(x - px) + abs(y - py)
            if d < md:
                md = d
        return md

    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not legal(nx, ny):
            continue

        cheb = max(abs(nx - ox), abs(ny - oy))
        man = abs(nx - ox) + abs(ny - oy)

        if nx == ox and ny == oy:
            score = -10**9 if is_pursuer else 10**9
        else:
            md_obs = min_dist_to_obstacles(nx, ny)
            # Greedy pursuit with obstacle-avoidance; evasion does the opposite.
            # Chebyshev is good for diagonal movement.
            if is_pursuer:
                score = (cheb * 1000 + man) - md_obs  # minimize
            else:
                score = (-cheb * 1000 - man) + md_obs  # maximize

        if best_score is None:
            best_score, best_move = score, (dx, dy)
        else:
            better = score < best_score if is_pursuer else score > best_score
            if better:
                best_score, best_move = score, (dx, dy)
            elif score == best_score:
                # Tie-break: prefer diagonal, then prefer smaller/larger manhattan accordingly, then stable (0,0).
                if diag_pref[(dx, dy)] != diag_pref[best_move]:
                    if is_pursuer:
                        # diagonal generally helps close distance
                        take = diag_pref[(dx, dy)] > diag_pref[best_move]
                    else:
                        take = diag_pref[(dx, dy)] >= diag_pref[best_move]
                else:
                    bn, by = best_move
                    bx, by_ = int(sx + bn), int(sy + by)
                    cur_m = man
                    best_m = abs(bx - ox) + abs(by_ - oy)
                    take = (cur_m < best_m) if is_pursuer else (cur_m > best_m)
                if take:
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]