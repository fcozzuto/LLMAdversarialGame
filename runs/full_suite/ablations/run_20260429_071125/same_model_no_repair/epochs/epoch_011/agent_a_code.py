def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    adj8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def obstacle_pen(x, y):
        p = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in occ:
                p += 2
        if (x, y) in occ:
            p += 10
        return p

    if resources:
        # Target: maximize how much better it is for us than for opponent; deterministic tie-break.
        best = None
        for rx, ry in resources:
            a = dist(ox, oy, rx, ry) - dist(sx, sy, rx, ry)
            key = (a, -dist(sx, sy, rx, ry), ry, rx)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
        best_move = (0, 0)
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            self_d = dist(nx, ny, tx, ty)
            opp_d = dist(ox, oy, tx, ty)
            val = (opp_d - self_d) * 10 - self_d - obstacle_pen(nx, ny)
            # Prefer staying closer while also avoiding giving opponent immediate advantage to same square.
            val += -dist(nx, ny, ox, oy) * 0.05
            key = (val, -self_d, obstacle_pen(nx, ny), -dx, -dy)
            if best_val is None or key > best_val:
                best_val = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # Fallback: move toward center to be robust when no resources are visible.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        self_d = dist(nx, ny, cx, cy)
        key = (-self_d - obstacle_pen(nx, ny) * 0.5, ny, nx, -dx, -dy)
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]