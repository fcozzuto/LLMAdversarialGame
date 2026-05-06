def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**9

    # Interception/pursuit objective: prefer moves that get closer to valuable "contested" targets
    # and simultaneously reduce our distance to the opponent.
    if resources:
        # Contested target proxy: resources near the midpoint between agents matter more.
        mx, my = (sx + ox) / 2.0, (sy + oy) / 2.0
        def contested(res):
            return md((res[0], res[1]), (mx, my))  # uses float coords safely

        targets = sorted(resources, key=contested)[:5]
    else:
        targets = [(w // 2, h // 2)]

    # Prefer reducing opponent distance and steering toward the best local target.
    # Add small deterministic tie-break toward diagonal/east/south to avoid jitter.
    tie_pref = {(0, 0): 0, (1, 0): 1, (0, 1): 2, (1, 1): 3, (-1, 0): 1, (0, -1): 2, (-1, -1): 3, (1, -1): 3, (-1, 1): 3}
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        opp_d = md((nx, ny), (ox, oy))
        # Evaluate best target for this move
        best_t = 10**9
        for tx, ty in targets:
            t_d = md((nx, ny), (tx, ty))
            # If the target is in the "front" direction from opponent, bias more.
            front_bias = 0
            if (tx - ox) * (sx - ox) >= 0 and (ty - oy) * (sy - oy) >= 0:
                front_bias = -1
            best_t = min(best_t, t_d + front_bias)

        # Higher is better: reduce target distance, and reduce opponent distance.
        val = (-best_t) + 0.6 * (-opp_d)

        if val > best_val or (val == best_val and tie_pref.get((dx, dy), 0) > tie_pref.get(best_move, 0)):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]