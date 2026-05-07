def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = None

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    target = None
    if resources:
        bestr = None
        for r in resources:
            rx, ry = r[0], r[1]
            k = dist((sx, sy), (rx, ry))
            if bestr is None or k < bestr[0]:
                bestr = (k, rx, ry)
        target = (bestr[1], bestr[2])

    if target is None:
        target = (w // 2, h // 2)

    for dx, dy, nx, ny in candidates:
        myd = dist((nx, ny), target)
        odd = dist((ox, oy), target)
        # Prefer getting closer than opponent; otherwise just minimize distance to target
        val = (myd >= odd, myd, abs(dx) + abs(dy))
        if best_val is None or val < best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]