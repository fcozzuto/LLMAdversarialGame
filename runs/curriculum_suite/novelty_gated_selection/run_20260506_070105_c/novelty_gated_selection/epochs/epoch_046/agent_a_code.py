def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def p2t(p, default):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            try:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    return (x, y)
            except Exception:
                pass
        return default

    sx, sy = p2t(observation.get("self_position", None), (0, 0))
    ox, oy = p2t(observation.get("opponent_position", None), (w - 1, h - 1))

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or []) if tuple(r) not in obstacles]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_step(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h:
            return nx, ny
        return x, y

    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    self_pos = (sx, sy)
    opp_pos = (ox, oy)

    # Strategic change vs interceptor: avoid racing the opponent; go for resources that are closer to us
    # but relatively far from the opponent (good "edge patrol" counterplay).
    best = None
    best_key = None
    for r in resources:
        r = (int(r[0]), int(r[1]))
        sd = abs(r[0] - sx) + abs(r[1] - sy)
        od = abs(r[0] - ox) + abs(r[1] - oy)
        # Lower is better: prioritize reachable first, then keep opponent farther.
        key = (sd, -(od), abs((r[0] - sx) - (r[1] - sy)), r[0], r[1])
        if best_key is None or key < best_key:
            best_key = key
            best = r

    tx, ty = best

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = clamp_step(sx, sy, dx, dy)
        if (nx, ny) in obstacles:
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        fod = abs(ox - nx) + abs(oy - ny)
        # Prefer reducing our distance to target; simultaneously increase separation from opponent.
        score = (nd, -fod, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]