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

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    for dx, dy, nx, ny in legal_moves(sx, sy):
        if nx == ox and ny == oy:
            return [int(dx), int(dy)]

    best = None
    best_score = None
    tie_d = None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx1, dy1, nx1, ny1 in legal_moves(sx, sy):
        worst_d = -1
        for _, _, nx2, ny2 in legal_moves(ox, oy):
            d = dist2(nx1, ny1, nx2, ny2)
            if d > worst_d:
                worst_d = d
        penalty = 0.02 if (dx1 == 0 and dy1 == 0) else 0.0
        center_pen = 0.0001 * dist2(nx1, ny1, cx, cy)
        score = worst_d + penalty + center_pen
        cur_d = dist2(nx1, ny1, ox, oy)
        if best_score is None or score < best_score or (score == best_score and cur_d < tie_d):
            best_score = score
            tie_d = cur_d
            best = (dx1, dy1)

    return [int(best[0]), int(best[1])]