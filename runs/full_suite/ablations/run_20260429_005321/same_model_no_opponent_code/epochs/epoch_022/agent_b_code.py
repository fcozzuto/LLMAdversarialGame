def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles if p is not None and len(p) >= 2)

    deltas = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]

    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If no resources, drift to center while staying safe from immediate approach.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (10**9, 10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not inside(nx, ny):
                continue
            v = (abs(nx - cx) + abs(ny - cy), md(nx, ny, ox, oy), dx, dy)
            if v < best:
                best = v
        return [best[2], best[3]]

    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            rx, ry = r[0], r[1]
            if (rx, ry) not in obst:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    # Choose resource where we are relatively closer than opponent.
    # Occasionally contest center to change trajectory when prior performance was poor.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    contest = (observation.get("turn_index", 0) % 4 == 0)

    if contest:
        tx, ty = int(round(cx)), int(round(cy))
        # Ensure target exists (may be obstacle); if so, fall back to resource targeting.
        if (tx, ty) in obst:
            contest = False

    if not contest:
        best = None
        for rx, ry in res:
            sdist = md(x, y, rx, ry)
            odist = md(ox, oy, rx, ry)
            # Maximize (odist - sdist), then prefer smaller sdist, then deterministic tie-break.
            score = (-(odist - sdist), sdist, rx, ry)
            if best is None or score < best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]

    # Move one step toward target; if blocked, pick the safe neighbor that minimizes distance to target
    # while also not allowing opponent to get dramatically closer.
    best = (10**9, 10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not inside(nx, ny):
            continue
        dt_self = md(nx, ny, tx, ty)
        dt_opp = md(ox, oy, tx, ty)
        # Penalize moves that bring us closer but let opponent close gap too much.
        # (Opponent moves next; we use a conservative, deterministic heuristic.)
        opp_after_proxy = md(nx, ny, ox, oy)  # proxy for potential contest
        v = (dt_self, abs(dt_opp - dt_self), opp_after_proxy, dx, dy)
        if v < best:
            best = (v[0], v[1], v[3], v[4])
    return [best[2], best[3]]