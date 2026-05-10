def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obs = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obs) if isinstance(obs, list) else set()
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def sgn(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny):
                c += 1
        return c

    dxo, dyo = ox - sx, oy - sy
    dom_x = abs(dxo) >= abs(dyo)
    want_dx = sgn(dxo) if dom_x else 0
    want_dy = sgn(dyo) if (not dom_x) else 0

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        base = dist2(nx, ny)
        cheb = max(abs(nx - ox), abs(ny - oy))
        manh = abs(nx - ox) + abs(ny - oy)
        mis = (0 if (dom_x and dx == want_dx) or (not dom_x and dy == want_dy) else 1)
        fn = free_neighbors(nx, ny)
        edge_risk = 1 if (nx in (0, w - 1) or ny in (0, h - 1)) else 0
        val = base * 10 + cheb * 2 + manh + mis * 8 - fn * 0.7 + edge_risk * 0.5
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]