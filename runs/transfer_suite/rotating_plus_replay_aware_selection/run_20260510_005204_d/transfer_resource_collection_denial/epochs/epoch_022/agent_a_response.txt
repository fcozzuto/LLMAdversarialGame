def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cd(x1, y1, x2, y2):  # Chebyshev distance
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a target that we can reach no later than opponent; if none, pick closest to us.
    best_t = None
    best_key = None
    for rx, ry in resources:
        myd = cd(sx, sy, rx, ry)
        opd = cd(ox, oy, rx, ry)
        # Prefer advantage, then closer, then central-ish tie-break
        adv = opd - myd
        center = -(abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        key = (adv >= 0, adv, -myd, center, -(rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # Evaluate moves; commit toward a target but avoid stepping into immediate opponent race when worse.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        myd_next = cd(nx, ny, tx, ty)
        # Estimate whether opponent will contest the same target if we don't arrive first.
        opd_now = cd(ox, oy, tx, ty)
        opd_next = opd_now - 1 if opd_now > 0 else 0
        contest_risk = 1 if myd_next >= opd_next else 0

        # If the move hits a resource, give it strong priority via remaining resource count proxy.
        hit = 1 if (nx, ny) in set(tuple(p) for p in resources) else 0
        # Lightweight bias to reduce dithering: prefer moves that reduce distance to target.
        dist_curr = cd(sx, sy, tx, ty)
        reduce = dist_curr - myd_next

        val = (hit * 100000) + (reduce * 1000) + ((-myd_next) * 10) + (-contest_risk * 500) + (-(nx + ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move