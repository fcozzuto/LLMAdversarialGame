def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))
    resources = toset(observation.get("resources"))
    if (not unclaimed) and resources:
        unclaimed = set(resources)
    if not unclaimed:
        return [0, 0]

    neigh4 = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    neigh8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    frontier = set()
    if selfT:
        for (x, y) in selfT:
            for dx, dy in neigh4:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in unclaimed:
                    frontier.add((nx, ny))
    candidates = frontier if frontier else unclaimed

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    bestv = -10**18
    for tx, ty in candidates:
        if (tx, ty) in obstacles:
            continue
        d1 = md(sx, sy, tx, ty)
        d2 = md(ox, oy, tx, ty)
        center = - (abs(tx - cx) + abs(ty - cy)) * 0.05
        lead = (d2 - d1)  # positive if we can arrive earlier
        block = 0
        if oppT:
            # slightly discourage cells deep inside opponent territory clusters
            if any((tx + dx, ty + dy) in oppT for dx, dy in neigh4):
                block = -0.25
        v = lead * 2.0 - d1 * 0.3 + center + block
        if v > bestv:
            bestv = v
            best = (tx, ty)

    tx, ty = best
    # propose direct step
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # if direct hits obstacle, choose best among 8-neighborhood + stay
    nx, ny = sx + dx, sy + dy
    if ok(nx, ny):
        return [dx, dy]

    # deterministic tie-break by fixed order in neigh8
    best_step = (0, 0)
    best_d = 10**9
    for ddx, ddy in neigh8:
        nnx, nny = sx + ddx, sy + ddy
        if not ok(nnx, nny):
            continue
        d = md(nnx, nny, tx, ty)
        if d < best_d or (d == best_d and (ddx, ddy) < best_step):
            best_d = d
            best_step = (ddx, ddy)
    return [best_step[0], best_step[1]]