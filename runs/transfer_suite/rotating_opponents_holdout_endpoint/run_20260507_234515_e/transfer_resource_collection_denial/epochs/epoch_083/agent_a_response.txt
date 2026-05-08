def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    if not resources:
        return [0, 0]
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    def ceil_dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, -10**18)
    for dx, dy in neigh:
        nx, ny = int(sx + dx), int(sy + dy)
        if not inb(nx, ny):
            continue
        best_for_move = 10**9
        for rx, ry in res:
            ds = ceil_dist(nx, ny, rx, ry)
            do = ceil_dist(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than opponent; slight preference for closer overall.
            val = (do - ds) * 100 - ds
            if val < best_for_move:
                best_for_move = val
        # Prefer higher val; tie-break deterministically by closeness to center-ish direction
        # Use secondary: minimal ds to nearest resource from the move.
        nearest_ds = min(ceil_dist(nx, ny, rx, ry) for rx, ry in res)
        score = best_for_move * 1000 - nearest_ds
        if score > best[1]:
            best = ((dx, dy), score)
    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]