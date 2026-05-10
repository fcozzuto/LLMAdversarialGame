def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []) or [])
    role = (observation.get("self_role", "") or "").lower()

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist2(x, y, x2, y2):
        dx = x - x2
        dy = y - y2
        return dx * dx + dy * dy

    def freedom(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    def corner_score(x, y):
        best = -1
        for cx, cy in corners:
            d = dist2(cx, cy, x, y)
            if d > best:
                best = d
        return best

    pursuer = ("purs" in role) or ("hunter" in role) or ("chaser" in role) or ("pursuer" in role)
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist2(nx, ny, ox, oy)
        f = freedom(nx, ny)
        cb = corner_score(nx, ny)
        # Small deterministic tie-break: earlier in deltas order via index.
        idx = deltas.index((dx, dy))
        if pursuer:
            val = (d, -f, -cb, idx)
        else:
            val = (-d, -f, -cb, idx)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]