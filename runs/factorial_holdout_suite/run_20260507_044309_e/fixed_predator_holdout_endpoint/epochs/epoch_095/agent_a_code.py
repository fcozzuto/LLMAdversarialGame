def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Target: closest for us, farthest for opponent (deterministic tie-breaks).
    best = None
    best_key = None
    for rx, ry in res:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        key = (ds - do, ds, do, rx, ry)
        if best is None or key < best_key:
            best = (rx, ry)
            best_key = key
    tx, ty = best

    def obstacle_adj_pen(nx, ny):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obstacles:
                    pen += 1
        return pen

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            deltas.append((dx, dy))

    opp_to_target = man(ox, oy, tx, ty)
    best_move = (0, 0)
    best_score = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        self_to_target = man(nx, ny, tx, ty)
        score = (opp_to_target - self_to_target) * 100 - self_to_target - obstacle_adj_pen(nx, ny)
        key = (-score, self_to_target, dx, dy)
        if best_score is None or key < best_key:
            best_score = score
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]