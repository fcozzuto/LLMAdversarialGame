def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inside(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                v = -(abs(nx - ox) + abs(ny - oy))
                if v > best[0]:
                    best = (v, dx, dy)
        return [best[1], best[2]]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    better = []
    fallback = []
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        if ds <= do:
            better.append((ds, do, rx, ry))
        else:
            fallback.append((ds - do, ds, rx, ry))

    if better:
        better.sort(key=lambda t: (t[0], t[2], t[3]))
        _, _, tx, ty = better[0]
    else:
        fallback.sort(key=lambda t: (t[0], t[2], t[3]))
        _, _, tx, ty = fallback[0]

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_self = dist((nx, ny), (tx, ty))
        d_opp = dist((ox, oy), (tx, ty))
        # Prefer reducing our distance; slightly prefer being closer than opponent to contest.
        v = -d_self + 0.03 * d_opp + (1e-6 * (nx * 8 + ny))
        # If we can reach immediately, strongly favor.
        if d_self == 0:
            v += 1000
        if v > best[0]:
            best = (v, dx, dy)

    return [best[1], best[2]]