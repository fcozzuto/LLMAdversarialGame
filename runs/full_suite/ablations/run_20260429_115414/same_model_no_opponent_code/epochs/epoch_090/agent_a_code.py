def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w)
        h = int(h)
    except:
        w, h = 8, 8
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    if resources:
        best = None
        for dx, dy, nx, ny in candidates:
            best_val = None
            for rx, ry in resources:
                ds = md(nx, ny, rx, ry)
                do = md(ox, oy, rx, ry)
                val = ds - 0.25 * do
                if best_val is None or val < best_val:
                    best_val = val
            if best is None or best_val < best[0] or (best_val == best[0] and (dx, dy) < best[1]):
                best = (best_val, (dx, dy))
        return [best[1][0], best[1][1]]

    # If no resources, deterministically drift toward opponent.
    best = None
    for dx, dy, nx, ny in candidates:
        d = md(nx, ny, ox, oy)
        if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
            best = (d, (dx, dy))
    return [best[1][0], best[1][1]]