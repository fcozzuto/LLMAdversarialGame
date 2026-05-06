def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def p2t(p, default):
        try:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
            else:
                return default
            if 0 <= x < w and 0 <= y < h:
                return (x, y)
        except Exception:
            pass
        return default

    sx, sy = p2t(observation.get("self_position", None), (0, 0))
    ox, oy = p2t(observation.get("opponent_position", None), (w - 1, h - 1))
    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or []) if tuple(r) not in obstacles]

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    opp_gx, opp_gy = 0, 0
    odx = 1 if opp_gx > ox else (-1 if opp_gx < ox else 0)
    ody = 1 if opp_gy > oy else (-1 if opp_gy < oy else 0)
    opp_next = (ox + odx, oy + ody)
    if not (0 <= opp_next[0] < w and 0 <= opp_next[1] < h) or opp_next in obstacles:
        opp_next = (ox, oy)

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nearest = 10**9
        for r in resources:
            d = abs(nx - r[0]) + abs(ny - r[1])
            if d < nearest:
                nearest = d
        block_dist = md((nx, ny), opp_next)
        opp_progress = abs((ny - oy))  # encourage denying their row-sweep by staying in their row lane
        key = (nearest, block_dist, opp_progress, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [best[1], best[2]]