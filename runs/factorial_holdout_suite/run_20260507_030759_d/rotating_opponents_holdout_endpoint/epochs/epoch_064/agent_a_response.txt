def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        return [0, 0]

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_key = None
    for c in res:
        sd = manh((c[0], c[1]), (sx, sy))
        od = manh((c[0], c[1]), (ox, oy))
        adv = od - sd  # positive means we are closer
        key = (-adv, sd, abs(c[0] - ox) + abs(c[1] - oy), c[0], c[1])
        if best_key is None or key < best_key:
            best_key = key
            best = c

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (-dx, dy), (dx, -dy), (0, 0)]
    for mx, my in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
        if (mx, my) not in candidates:
            candidates.insert(0, (mx, my))
    # deterministic preference among candidates:
    candidates = sorted(set(candidates), key=lambda d: (d[0] != dx, d[1] != dy, -d[0], -d[1]))

    best_step = None
    best_val = None
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        step_sd = manh((nx, ny), (tx, ty))
        step_od = manh((nx, ny), (ox, oy))
        # Prefer reducing our distance to target, and if tied prefer increasing opponent distance.
        val = (step_sd, -step_od, (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty), mx, my)
        if best_val is None or val < best_val:
            best_val = val
            best_step = (mx, my)

    if best_step is None:
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]