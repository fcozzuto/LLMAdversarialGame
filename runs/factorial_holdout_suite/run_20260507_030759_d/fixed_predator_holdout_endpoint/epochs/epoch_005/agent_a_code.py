def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw) if obstacles_raw else set()

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_mv = [0, 0]
    best_val = None

    if not resources:
        return best_mv

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Evaluate: best advantage over any reachable resource.
        val = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; break ties by smaller my distance.
            cand = (od - md, -md, -rx, -ry)
            if val is None or cand > val:
                val = cand
        if val is None:
            continue
        if best_val is None or val > best_val:
            best_val = val
            best_mv = [dx, dy]

    return best_mv