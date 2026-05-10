def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)
    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_pursuer = ("purs" in self_role) and ("evad" not in self_role)
    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def neighbors(x, y):
        res = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inside(nx, ny) and (nx, ny) not in obs:
                res.append((nx, ny))
        return res

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    def corner_bias(x, y):
        return max(d2(x, y, cx, cy) for cx, cy in corners)

    def opp_best_to_capture(tgtx, tgty):
        best = None
        bestd = None
        for nx, ny in neighbors(ox, oy):
            dd = d2(nx, ny, tgtx, tgty)
            if best is None or dd < bestd:
                bestd = dd
                best = (nx, ny)
        return best

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue

        dist = d2(nx, ny, ox, oy)
        mob = len(neighbors(nx, ny))
        if self_pursuer:
            val = -dist + 0.15 * mob - 0.01 * (abs(nx - ox) + abs(ny - oy))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]
        else:
            pred = opp_best_to_capture(nx, ny)
            trap_pen = 0.0
            if pred is not None and pred[0] == nx and pred[1] == ny:
                trap_pen = 100000.0
            val = dist + 0.12 * mob + 0.05 * corner_bias(nx, ny) - trap_pen - 0.01 * (abs(nx - ox) + abs(ny - oy))
            if best_val is None or val > best_val:
                best_val = val
                best_move = [dx, dy]
    return best_move