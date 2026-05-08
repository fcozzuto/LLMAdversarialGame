def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = []
    for rx, ry in resources:
        if (rx, ry) not in obs:
            res.append((rx, ry))
    if not res:
        return [0, 0]

    best = None
    for dx, dy in legal:
        ns = (sx + dx, sy + dy)

        # if we land on a resource, prioritize strongly
        on_res = 1 if ns in res else 0

        # nearest resource distances for self and opponent (after our move)
        sd = 10**9
        od = 10**9
        close_self = 0
        for r in res:
            d = md(ns, r)
            if d < sd:
                sd = d
            if d <= 2:
                close_self += 1
            do = md((ox, oy), r)
            if do < od:
                od = do

        # value: prefer being closer than opponent + local resource density; also avoid tight parity
        value = (on_res * 10_000) + (od - sd) + (close_self * 2) - (sd * 0.1)

        # deterministic tie-break: lexicographic on move
        key = (value, -close_self, -on_res, -dx, -dy)
        if best is None or key > best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]