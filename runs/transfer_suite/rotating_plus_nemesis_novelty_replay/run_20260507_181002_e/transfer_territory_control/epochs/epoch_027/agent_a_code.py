def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    x, y = int(p[0]), int(p[1])
                    if 0 <= x < w and 0 <= y < h:
                        s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    resources = toset(observation.get("resources"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def best_target(cands):
        bx = by = None
        bd = 10**9
        for tx, ty in cands:
            d = abs(sx - tx) + abs(sy - ty)
            if d < bd:
                bd, bx, by = d, tx, ty
        return (bx, by, bd)

    target_set = resources if resources else unclaimed
    if target_set:
        tx, ty, _ = best_target(target_set)
    else:
        tx, ty = (w // 2), (h // 2)

    def score_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return -10**9
        d = abs(nx - tx) + abs(ny - ty)
        adv = -(abs(nx - ox) + abs(ny - oy)) * 0.1
        return -d + adv

    best = None
    best_sc = -10**18
    for dx, dy in neigh:
        sc = score_move(dx, dy)
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]