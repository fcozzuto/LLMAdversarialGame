def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    legal = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource: prefer close to us, penalize if opponent is closer.
    if resources:
        best = None
        best_score = None
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # If opponent is closer, make it less attractive; also break ties deterministically.
            score = ds + (2.0 if do < ds else 0.0) + 0.001 * (tx + ty)
            if best_score is None or score < best_score:
                best_score = score
                best = (tx, ty)
        tx, ty = best
    else:
        # If no resources, drift toward center while separating from opponent.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Choose move minimizing distance to target, while maximizing separation from opponent if tied.
    best_mv = (0, 0)
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)

        # Small preference to keep moving (avoid staying if equivalent).
        stay_pen = 0.1 if dx == 0 and dy == 0 else 0.0

        # If moving makes opponent closer to the same target than we are, add a mild penalty.
        opp_after = cheb(ox, oy, tx, ty)
        us_after = d_t
        block_pen = 0.2 if opp_after < us_after else 0.0

        val = d_t + stay_pen + block_pen - 0.01 * d_o
        if best_val is None or val < best_val:
            best_val = val
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]