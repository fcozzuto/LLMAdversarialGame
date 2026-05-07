def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    legal = []
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))

    if not legal or not resources:
        return [0, 0]

    best = None
    best_move = (0, 0)

    for dx, dy in legal:
        ns = (sx + dx, sy + dy)
        # Evaluate best resource for "race/denial" after this move.
        # Higher is better: advantage of self over opponent, then closeness.
        local_best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            tr = (rx, ry)
            if tr in obstacles:
                continue
            self_d = dist(ns, tr)
            opp_d = dist((ox, oy), tr)
            # also consider tighter diagonal distance as a proxy
            self_c = cheb(ns, tr)
            # Prefer resources we can reach sooner; strongly deny those opponent is much closer to.
            val = (opp_d - self_d) * 10 - self_c
            # If equal, deterministic: smaller target coord
            tie = (opp_d - self_d, -self_d, -self_c, rx, ry)
            key = (val, tie)
            if local_best is None or key > local_best[0]:
                local_best = (key, r)
        if local_best is None:
            local_key = (-10**18, (0, 0, 0, 0, 0))
        else:
            local_key = local_best[0]
        move_key = (local_key[0], local_key[1], -abs(dx), -abs(dy), dx, dy)
        if best is None or move_key > best:
            best = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]