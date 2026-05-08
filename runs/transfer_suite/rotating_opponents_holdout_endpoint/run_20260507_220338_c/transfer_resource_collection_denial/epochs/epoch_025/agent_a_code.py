def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    res_set = set(tuple(p) for p in resources)

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    def best_target():
        best = None
        best_key = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            # prefer cells where we are sooner; also prefer resources closer to both (less contest wandering)
            key = (opd - myd, -(myd + opd), -rx - ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = best_target()
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # local tie-breaker: try to reduce own distance, but if opponent can reach much sooner, prioritize denier
    myd_now = md(sx, sy, tx, ty)
    opd_now = md(ox, oy, tx, ty)

    best = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)
        # deny pressure: if opponent is ahead for this target, reduce their effective lead via blocking distance
        deny = 0
        if opd + 1 < myd:
            deny = (opd + 1 - myd) * 3

        gain = 0
        if (nx, ny) in res_set:
            gain = 100

        # also prefer moving away from opponent when target is heavily contested
        contest = 0
        if opd_now + 1 < myd_now:
            contest = md(nx, ny, ox, oy)

        val = (gain, -deny, -myd, -contest, -abs((nx - tx)) - abs((ny - ty)))
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]