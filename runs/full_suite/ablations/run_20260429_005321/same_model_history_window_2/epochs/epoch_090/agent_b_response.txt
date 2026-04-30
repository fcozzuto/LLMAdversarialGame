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

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick a target that we can reach at least as fast as opponent; if none, pick best gap.
    tx = ty = None
    best = None
    if resources:
        for rx, ry in resources:
            d1 = cheb(sx, sy, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            gap = d2 - d1  # positive favors us
            # Encourage grabbing closer resources and deny obvious opponent advantage.
            key = (0, -d1, -gap)
            if gap >= 0:
                key = (1, -d1, -gap)
            if best is None or key > best:
                best = key
                tx, ty = rx, ry
    else:
        # No visible resources: push toward opponent's side of the board midline for future contest.
        # Deterministic: target depends on opponent quadrant.
        tx = 0 if ox > (w - 1) // 2 else w - 1
        ty = 0 if oy > (h - 1) // 2 else h - 1

    # Greedy step toward target with obstacle pressure and opponent interference.
    # Also avoid stepping into squares that reduce our distance while increasing opponent distance too little.
    if tx is None:
        return [0, 0]

    best_m = (0, 0)
    best_v = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        # obstacle proximity penalty (deterministic, local)
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    near_obs += 1
        # Prefer moves that improve our distance most and (secondarily) don't give opponent an immediate advantage.
        opp_future_gap = d_opp - cheb(nx, ny, tx, ty)
        v = (20 * opp_future_gap) - (5 * d_self) - (3 * near_obs)
        if (nx, ny) == (tx, ty):
            v += 1000
        if v > best_v:
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]