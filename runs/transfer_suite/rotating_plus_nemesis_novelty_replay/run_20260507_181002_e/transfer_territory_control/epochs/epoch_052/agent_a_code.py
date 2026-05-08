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

    if unclaimed:
        candidates = list(unclaimed)
    else:
        candidates = list(oppT)

    if not candidates:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_val = -10**18

    for tx, ty in candidates:
        if (tx, ty) in obstacles:
            continue
        ds = dist(sx, sy, tx, ty)
        do = dist(ox, oy, tx, ty)
        dc = abs(tx - cx) + abs(ty - cy)  # far from center
        # Prefer claiming outer ring, keep away from opponent, and get there reasonably fast.
        val = 6.0 * dc + 2.0 * do - 1.2 * ds
        if (tx, ty) in oppT:
            val += 1.5  # opportunistically capture if no unclaimed pressure exists
        if (tx, ty) in selfT:
            val -= 0.5
        if val > best_val or (val == best_val and (best is None or (tx, ty) < best)):
            best_val = val
            best = (tx, ty)

    tx, ty = best
    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    move_order = [(dx, dy) for dy in dys for dx in dxs]  # deterministic
    best_move = (0, 0)
    best_mval = -10**18

    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        # Greedy: reduce distance to target, and avoid getting too close to opponent.
        mval = -dist(nx, ny, tx, ty) + 0.2 * dist(nx, ny, ox, oy)
        if mval > best_mval:
            best_mval = mval
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]