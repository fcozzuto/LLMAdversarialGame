def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    def legal(nx, ny): return inside(nx, ny) and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    opp = (ox, oy)
    me = (sx, sy)

    # If no resources, just maximize distance from opponent to avoid contested pickup paths.
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            if (nx, ny) == opp:
                score = -10**12
            else:
                score = dist((nx, ny), opp) + (0 if (nx, ny) == me else 0)
            if score > best_score:
                best_score = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose a move by (1) best "winning" target (me vs opponent), (2) closeness to that target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if (nx, ny) == opp:
            continue

        my_pos = (nx, ny)
        # Determine the target where I have maximal distance advantage (opponent further than me).
        best_adv = -10**18
        best_t = resources[0]
        for r in resources:
            d_me = dist(my_pos, r)
            d_op = dist(opp, r)
            adv = d_op - d_me  # positive means I'm closer
            if adv > best_adv or (adv == best_adv and (d_me, r) < (dist(my_pos, best_t), best_t)):
                best_adv = adv
                best_t = r

        d_best_me = dist(my_pos, best_t)
        d_best_op = dist(opp, best_t)
        # Strongly prefer positive advantage; otherwise still go toward nearest resource that minimizes opponent capture likelihood.
        advantage_term = best_adv * 50
        closeness_term = -d_best_me * 5
        opponent_pressure = -max(0, d_best_op - d_best_me) * 2 - dist(my_pos, opp) * 0.2

        # Small bias toward moving to a resource cell if adjacent.
        immediate_pick = 20 if my_pos in resources else 0

        score = advantage_term + closeness_term + opponent_pressure + immediate_pick

        # Deterministic tie-break: prefer smallest |dx|+|dy| then lexicographic.
        tie_key = (abs(dx) + abs(dy), dx, dy)
        cur_tie = (abs(best[0]) + abs(best[1]), best[0], best[1])
        if score > best_score or (score == best_score and tie_key < cur_tie):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]