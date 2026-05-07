def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # If no resources, move toward the center corner-favoring deterministically
    if not resources:
        cx, cy = w // 2, h // 2
        best = min(moves, key=lambda m: dist((sx + m[0], sy + m[1]), (cx, cy)))
        return [best[0], best[1]]

    # Pick best resource by taking first that we can reach sooner; otherwise by largest time advantage (opponent - self).
    best_r = None
    best_key = None
    for rx, ry in resources:
        d_self = dist((sx, sy), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        margin = d_opp - d_self  # positive means we are closer/equal
        key = (0 if d_self <= d_opp else 1, -margin, d_self, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    # Choose move that minimizes distance to target; break ties by also pushing away from opponent when possible.
    best_m = None
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d_to = dist((nx, ny), (tx, ty))
        d_opp_next = dist((nx, ny), (ox, oy))
        d_opp_cur = dist((sx, sy), (ox, oy))
        key = (d_to, 0 if d_opp_next >= d_opp_cur else 1, -d_opp_next, dx, dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]