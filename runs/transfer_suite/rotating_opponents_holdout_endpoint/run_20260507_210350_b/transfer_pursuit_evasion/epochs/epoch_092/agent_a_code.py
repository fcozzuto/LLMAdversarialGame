def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    self_role = observation.get("self_role") or "pursuer"
    if self_role not in ("pursuer", "evader"):
        self_role = "pursuer"

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_val = None

    for i, (dx, dy) in enumerate(moves):
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = abs(nx - ox) + abs(ny - oy)

        # avoid being too close to opponent if evader; help if pursuer
        # also avoid corners/edges that reduce options deterministically
        edge_pen = (nx == 0) + (nx == w - 1) + (ny == 0) + (ny == h - 1)
        # small obstacle proximity penalty (local)
        near_obs = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if (tx, ty) in obs:
                near_obs += 1

        # deterministic scoring
        if self_role == "pursuer":
            val = (d, edge_pen * 0.05 + near_obs * 0.01, i)
            want = "min"
        else:  # evader
            val = (-d, edge_pen * 0.05 + near_obs * 0.01, i)
            want = "min"

        if best is None:
            best, best_val = (dx, dy), val
        else:
            if val < best_val:
                best, best_val = (dx, dy), val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]