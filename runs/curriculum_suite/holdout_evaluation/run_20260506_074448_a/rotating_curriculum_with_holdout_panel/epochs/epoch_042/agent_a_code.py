def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((int(p[0]), int(p[1])) for p in obstacles)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if resources:
        tx, ty = min(resources, key=lambda r: man(sx, sy, r[0], r[1]))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = None
    bestv = -10**30
    distT0 = man(sx, sy, tx, ty)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        dT = man(nx, ny, tx, ty)
        dO = man(nx, ny, ox, oy)
        # Prefer getting closer to target, avoid letting opponent get too close, and slightly prefer safety.
        v = (distT0 - dT) * 10 - dO * 0.2 - (0.001 * (nx * nx + ny * ny))
        # If stepping onto a resource, strongly prefer it.
        if resources and any(nx == r[0] and ny == r[1] for r in resources):
            v += 1000
        if v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]