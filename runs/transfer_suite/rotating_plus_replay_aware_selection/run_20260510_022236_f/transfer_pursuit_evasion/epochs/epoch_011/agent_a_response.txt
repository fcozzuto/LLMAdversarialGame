def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    role = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in role) or ("pursuer" in role) or ("hunter" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    phase = int(observation.get("turn_index", 0)) % 4
    escape_corner = corners[phase]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def score_move(nx, ny):
        if not ok(nx, ny):
            return -10**9
        d2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        corner_d2 = (nx - escape_corner[0]) * (nx - escape_corner[0]) + (ny - escape_corner[1]) * (ny - escape_corner[1])
        # mobility: avoid trapping
        mob = 0
        for dx, dy in moves:
            tx, ty = nx + dx, ny + dy
            if ok(tx, ty):
                mob += 1
        # obstacle proximity penalty (soft)
        prox = 0
        for ax, ay in obs:
            dd = abs(nx - ax) + abs(ny - ay)
            if dd <= 2:
                prox += (3 - dd)
        if pursuer:
            # minimize distance; keep mobility high; discourage risky obstacle crowding
            return (-d2 * 2 + mob * 4 - prox * 3 + corner_d2 * -0.02)
        else:
            # maximize distance; bias toward a deterministic escape corner; keep mobility
            return (d2 * 2 + mob * 4 + corner_d2 * 0.03 - prox * 3)

    best = None
    best_s = -10**18
    # deterministic tie-break: iterate moves in fixed order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        s = score_move(nx, ny)
        if s > best_s:
            best_s = s
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]