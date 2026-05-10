def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose a resource we can secure: prioritize (opp_advantage - self_advantage)
    best = None
    best_r = None
    sprint = int(observation.get("remaining_resource_count", len(res)) or len(res)) <= 6
    for x, y in res:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # If sprinting, value short ds more strongly
        secure = do - ds  # higher is better (we arrive earlier)
        # If ds ties, prefer smaller ds and then stable tie-break by coordinates
        key = (-secure, ds * (2 if sprint else 1), x + 17 * y)
        if best is None or key < best:
            best = key
            best_r = (x, y)

    tx, ty = best_r
    cx = tx - sx
    cy = ty - sy
    step_candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                continue
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                # Prefer moves reducing chebyshev distance; tie-break for diagonal and closer alignment
                d_before = cheb(sx, sy, tx, ty)
                d_after = cheb(nx, ny, tx, ty)
                align = (abs(cx) + abs(cy) - (abs(tx - nx) + abs(ty - ny)))
                diag = 1 if dx != 0 and dy != 0 else 0
                key = (d_after - d_before, -diag, -align, abs(cx - dx) + abs(cy - dy), nx + 31 * ny)
                step_candidates.append((key, [dx, dy]))

    if step_candidates:
        step_candidates.sort(key=lambda t: t[0])
        return step_candidates[0][1]
    return [0, 0]