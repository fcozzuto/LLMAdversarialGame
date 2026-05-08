def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x, y):
        dx = x - ox
        dy = y - oy
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    role = str(observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in role) or ("pursuer" in role)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            val = -10**9 if is_pursuer else 10**9
        else:
            d = cheb(nx, ny)
            # If pursuer, minimize distance; if evader, maximize distance.
            # Add mild bias to keep away from edges/obstacles while staying deterministic.
            edge_pen = (0 if 0 < nx < w - 1 else 1) + (0 if 0 < ny < h - 1 else 1)
            obs_pen = 1 if (nx + dx, ny + dy) in obstacles else 0
            if is_pursuer:
                val = -d * 100 - edge_pen * 3 - obs_pen
            else:
                val = d * 100 - edge_pen * 3 - obs_pen
        if best is None or (val > best_val):
            best_val = val
            best = [dx, dy]
    return [int(best[0]), int(best[1])]