def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if resources:
        # Pick target where our chebyshev advantage is maximized.
        best_t = None
        best_m = -10**9
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd
            # Prefer nearer centrality among equal margins to stabilize.
            centr = -cheb(rx, ry, cx, cy)
            key = margin * 1000 + centr
            if key > best_m:
                best_m = key
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = cx, cy

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Core: increase our advantage and progress to target.
        val = (opd - myd) * 100 - myd
        # Small preference to move away from opponent when not improving much.
        opp_close = cheb(nx, ny, ox, oy)
        val += opp_close * 0.5
        # Tie-break: deterministic toward center then toward staying.
        val += -cheb(nx, ny, cx, cy) * 0.1
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move