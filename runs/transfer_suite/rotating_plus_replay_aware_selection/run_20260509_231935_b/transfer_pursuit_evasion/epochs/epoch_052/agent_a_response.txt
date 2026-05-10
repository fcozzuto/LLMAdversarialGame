def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or (("pursuer" in opp_role) and ("evader" in self_role or "pursuit" in self_role))

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    neigh = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def free_count(x, y):
        c = 0
        for dx, dy in neigh:
            nx, ny = x + dx, y + dy
            if legal(nx, ny):
                c += 1
        return c

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Primary objective: evade (maximize distance) or pursue (minimize distance)
        primary = d2 if is_evader else -d2

        # Secondary objective: keep mobility (avoid getting trapped behind obstacles)
        f = free_count(nx, ny)

        # Tiebreaker: prefer moving toward/away from the opposite/farthest corner deterministically
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        if is_evader:
            target = max(corners, key=lambda t: (t[0] - ox) * (t[0] - ox) + (t[1] - oy) * (t[1] - oy))
            corner_score = (nx - target[0]) * (nx - target[0]) + (ny - target[1]) * (ny - target[1])
        else:
            target = min(corners, key=lambda t: (t[0] - ox) * (t[0] - ox) + (t[1] - oy) * (t[1] - oy))
            corner_score = -((nx - target[0]) * (nx - target[0]) + (ny - target[1]) * (ny - target[1]))

        key = (primary, f, corner_score, -abs(dx) - abs(dy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]