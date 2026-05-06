def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0] or 0), int(sp[1] or 0)
    ox, oy = int(op[0] or 0), int(op[1] or 0)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(ax, ay, bx, by):
        ax = ax - bx
        if ax < 0:
            ax = -ax
        ay = ay - by
        if ay < 0:
            ay = -ay
        return ax + ay

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if inside(x, y):
            res.append((x, y))
    if not res:
        cx, cy = w // 2, h // 2
        options = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if inside(sx + dx, sy + dy)]
        best = None
        bestv = -10**9
        for dx, dy in options:
            nx, ny = sx + dx, sy + dy
            v = (dist(nx, ny, ox, oy) - dist(sx, sy, ox, oy)) - 0.05 * dist(nx, ny, cx, cy)
            if v > bestv or (v == bestv and (best is None or (dx, dy) < best)):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Interceptor/opportunistic: move to improve our claim on a resource where opponent is relatively disadvantaged,
    # plus a bias to prevent getting boxed in near obstacles/opponent.
    options = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if inside(sx + dx, sy + dy)]
    cx, cy = w // 2, h // 2

    best = None
    bestv = -10**18
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        # If we are closer to a high-value resource than the opponent, strongly prefer.
        v = -0.03 * dist(nx, ny, cx, cy) - 0.02 * dist(nx, ny, ox, oy)
        for rx, ry in res:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; penalize those opponent can reach faster.
            # Also small term to prefer reducing our distance when close.
            claim = 2 * od - sd
            if claim >= 0:
                v += 40 + 5 * claim - 0.5 * sd
            else:
                v += 2 + 0.5 * claim
        # Small anti-standoff: if opponent is adjacent, move to widen separation.
        if dist(nx, ny, ox, oy) == 1:
            v += 25
        if v > bestv or (v == bestv and (best is None or (dx, dy) < best)):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]