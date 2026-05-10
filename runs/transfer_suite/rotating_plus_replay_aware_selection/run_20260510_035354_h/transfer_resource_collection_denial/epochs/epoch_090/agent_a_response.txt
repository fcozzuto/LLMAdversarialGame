def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    opp_role = (observation.get("opponent_role", "") or "").lower()

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cand = None
    best = None
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive => we are closer (good)
        bonus = 0
        if (rx == ox or ry == oy):
            bonus += 0.25 if "shadow" in opp_role else 0.1
        # Prefer reachable sooner; also prefer being ahead even if both are close.
        key = (adv + bonus, -ds, -cheb(ox, oy, sx, sy))
        if best is None or key > best:
            best = key
            cand = (rx, ry)

    rx, ry = cand
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    # Obstacle-aware step selection (no full search)
    primary = (sx + dx, sy + dy)
    if (0 <= primary[0] < w and 0 <= primary[1] < h and primary not in obs):
        return [dx, dy]

    # Try axis-aligned alternatives deterministically
    options = []
    if dx != 0:
        options.append((sx + dx, sy, dx, 0))
    if dy != 0:
        options.append((sx, sy + dy, 0, dy))
    options.append((sx, sy, 0, 0))

    for nx, ny, ddx, ddy in options:
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [ddx, ddy]

    return [0, 0]