def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {tuple(p) for p in obstacles}

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Choose target resource where we are (most) ahead over the opponent, then nearest tie-breakers.
    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        ahead = od - sd
        # Prefer immediate pickup, then biggest ahead, then smallest sd.
        if sd == 0:
            key = (10**9, 0, rx, ry)
        else:
            key = (ahead, -sd, rx, ry)
        if best is None or key > best[0]:
            best = (key, rx, ry, sd, od)
    _, tx, ty, _, oppd = best

    # If target is blocked, pick next best deterministically by scanning resources again.
    if (tx, ty) in obs:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            ahead = od - sd
            if sd == 0:
                key = (10**9, 0, rx, ry)
            else:
                key = (ahead, -sd, rx, ry)
            if best is None or key > best[0]:
                best = (key, rx, ry, sd, od)
        if best is None:
            return [0, 0]
        _, tx, ty, _, oppd = best

    # Evaluate one-step moves: maximize (oppd - new_self_dist), avoid obstacles, avoid walls, slight preference for staying closer to target.
    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            val = -10**15
        else:
            selfd = man(nx, ny, tx, ty)
            # Big reward for picking up target.
            if selfd == 0:
                pickup = 10**9
            else:
                pickup = 0
            # Prefer staying ahead of opponent reachability proxy.
            reach_term = (oppd - selfd) * 1000
            wall_safety = 0
            # Mild bias: don't drift away from our current best progress direction.
            progress = -selfd
            # Encourage central-ish movement to reduce dead-ends.
            center_bias = -((nx - (gw - 1) / 2) ** 2 + (ny - (gh - 1