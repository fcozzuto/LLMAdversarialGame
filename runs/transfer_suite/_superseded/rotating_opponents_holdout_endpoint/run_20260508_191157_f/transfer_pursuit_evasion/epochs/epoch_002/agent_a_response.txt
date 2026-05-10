def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal_moves(x, y):
        out = []
        for dx in dxs:
            for dy in dys:
                nx, ny = x + dx, y + dy
                if in_bounds(nx, ny) and (nx, ny) not in obs:
                    out.append((dx, dy, nx, ny))
        if not out:
            out = [(0, 0, x, y)]
        return out

    # If we can capture immediately, do it.
    for dx, dy, nx, ny in legal_moves(sx, sy):
        if nx == ox and ny == oy:
            return [int(dx), int(dy)]

    best_move = (0, 0)
    best_val = None

    # Two-ply: we minimize our distance; opponent (adversarial) maximizes it.
    for dx1, dy1, nx1, ny1 in legal_moves(sx, sy):
        # Our distance after our move (baseline tie-breaker)
        base = (nx1 - ox) * (nx1 - ox) + (ny1 - oy) * (ny1 - oy)

        worst = -1
        for _, _, nx2, ny2 in legal_moves(ox, oy):
            d = (nx1 - nx2) * (nx1 - nx2) + (ny1 - ny2) * (ny1 - ny2)
            if d > worst:
                worst = d

        # Prefer smaller worst-case distance; then prefer smaller baseline; then prefer non-stay.
        non_stay = 0 if (dx1 == 0 and dy1 == 0) else -1
        key = (worst, base, non_stay)
        if best_val is None or key < best_val:
            best_val = key
            best_move = (dx1, dy1)

    return [int(best_move[0]), int(best_move[1])]