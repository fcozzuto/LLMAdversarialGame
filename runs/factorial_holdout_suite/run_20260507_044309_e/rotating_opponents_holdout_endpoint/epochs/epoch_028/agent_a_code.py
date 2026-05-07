def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources or (sx, sy) in obstacles:
        return [0, 0]
    if (sx, sy) in resources:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        if sd <= od:
            lead = od - sd
            key = (-lead, sd, rx + 13 * ry, rx, ry)
        else:
            gap = sd - od
            key = (gap * 4 + 1, od, sd, rx + 13 * ry, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (nx, ny) in obstacles:
                continue
            if (nx, ny) != (tx, ty) and (nx, ny) == (ox, oy):
                continue
            dist = md(nx, ny, tx, ty)
            # Prefer moving closer to target; tie-break by avoiding opponent proximity slightly.
            opp_dist = md(nx, ny, ox, oy)
            # Also bias toward higher y then x for deterministic behavior.
            key = (dist, -opp_dist, -ny, -nx, dx, dy)
            candidates.append((key, [dx, dy]))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    return candidates[0][1]