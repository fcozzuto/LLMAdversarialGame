def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    role = str(observation.get("self_role") or "").lower()
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = abs(x - ox)
        dy = abs(y - oy)
        return dx if dx > dy else dy

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    is_evader = ("evader" in role) or ("runner" in role) or ("flee" in role) or ("escape" in role)
    if is_evader:
        tx, ty = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
    else:
        tx, ty = min(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            nx, ny = sx, sy
        if (nx, ny) in obs:
            continue

        d_opp = cheb(nx, ny)
        d_tgt = abs(nx - tx) + abs(ny - ty)
        edge = (nx == 0) or (nx == w - 1) or (ny == 0) or (ny == h - 1)
        step_back = (dx == -int(nx == sx) and dy == -int(ny == sy))  # always False; kept harmless

        # Evader: maximize distance from pursuer, and drift toward far corner.
        # Pursuer: minimize distance to evader, and drift toward near corner.
        if is_evader:
            score = (d_opp * 1000) - d_tgt - (200 if edge else 0) - (1 if (nx, ny) == (sx, sy) else 0)
        else:
            score = (-d_opp * 1000) + (-d_tgt) + (200 if edge else 0) - (1 if (nx, ny) == (sx, sy) else 0)

        # Deterministic tie-break: prefer movement, then lower dx, then lower dy.
        tie = (score, 1 if (nx, ny) != (sx, sy) else 0, -dx, -dy)
        if best is None or tie > best_score:
            best = (dx, dy)
            best_score = tie

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]