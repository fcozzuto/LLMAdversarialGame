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

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if res:
        best = None
        for dx, dy, nx, ny in moves:
            d = 10**9
            for x, y in res:
                dd = abs(nx - x) + abs(ny - y)
                if dd < d:
                    d = dd
            # tie-breaker favors moving closer to opponent less aggressively
            score = (d, abs(nx - ox) + abs(ny - oy), dx, dy)
            if best is None or score < best[0]:
                best = (score, (dx, dy))
        return [best[1][0], best[1][1]]

    # No visible resources: move toward center away from opponent if possible
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    for dx, dy, nx, ny in moves:
        score = (abs(nx - cx) + abs(ny - cy), -(abs(nx - ox) + abs(ny - oy)), dx, dy)
        if best is None or score < best[0]:
            best = (score, (dx, dy))
    return [best[1][0], best[1][1]]