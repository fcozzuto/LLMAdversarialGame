def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dxs = (-1, 0, 1)
    legal = []
    for dx in dxs:
        for dy in dxs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))

    if not legal:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set:
        return [0, 0]
    if not resources:
        # Head toward opponent distance to reduce being blocked
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dself = abs(nx - ox) + abs(ny - oy)
            cand = (-dself, dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[1], best[2]]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # For each candidate move, pick the best resource by "can arrive first" then closeness.
    best_overall = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_for_move = None
        for rx, ry in resources:
            self_d = manh(nx, ny, rx, ry)
            opp_d = manh(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; then minimize our distance.
            # Add slight bias toward cells that are closer to any resource overall.
            min_self = min(manh(nx, ny, r2x, r2y) for (r2x, r2y) in resources)
            cand = (opp_d - self_d, -self_d, -min_self, -rx, -ry)
            if best_for_move is None or cand > best_for_move:
                best_for_move = cand
        overall = (best_for_move, dx, dy)
        if best_overall is None or overall > best_overall:
            best_overall = overall

    return [best_overall[1], best_overall[2]]