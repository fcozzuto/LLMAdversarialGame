def choose_move(observation):
    w = int(observation.get("grid_width", 0))
    h = int(observation.get("grid_height", 0))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    unclaimed = []
    for p in (observation.get("unclaimed_cells") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                unclaimed.append((x, y))

    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0), (0, 0)]
    if not w or not h:
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if unclaimed:
        tx, ty = min(unclaimed, key=lambda p: (dist(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        tx, ty = ox, oy

    best = None
    for dx, dy in dirs:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inb(nx, ny):
            continue
        v = dist(nx, ny, tx, ty)
        if best is None or v < best[0] or (v == best[0] and (dx, dy) < best[1]):
            best = (v, (dx, dy))
    return list(best[1]) if best is not None else [0, 0]