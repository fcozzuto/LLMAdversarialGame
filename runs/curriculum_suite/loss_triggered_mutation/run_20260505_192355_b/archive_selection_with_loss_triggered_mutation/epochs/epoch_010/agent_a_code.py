def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Pick the resource where we have the biggest distance advantage; tie-break by closer and stable ordering.
    best = None
    for tx, ty in sorted(res):
        myd = md(sx, sy, tx, ty)
        opd = md(ox, oy, tx, ty)
        # Larger advantage first: (opd - myd). If equal, smaller myd.
        key = (-(opd - myd), myd, tx, ty)
        if best is None or key < best[0]:
            best = (key, (tx, ty))
    tx, ty = best[1]

    # Consider our 9 possible moves, avoid obstacles, prefer those that minimize our distance to target,
    # and secondarily keep away from opponent to reduce chance of being out-contested nearby.
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        myd = md(nx, ny, tx, ty)
        opd_next = md(nx, ny, ox, oy)
        # Primary: closer to target; Secondary: keep farther from opponent; Tertiary: deterministic tie-break.
        key = (myd, -opd_next, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, [dx, dy])
    return best_move[1]