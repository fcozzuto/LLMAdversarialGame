def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def dist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonal allowed)

    valid = []
    for r in resources:
        x, y = r[0], r[1]
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    tr = observation.get("turns_remaining", 0)
    few = tr <= 6 or observation.get("remaining_resource_count", len(valid)) <= 3

    best = None
    best_val = -10**9
    for rx, ry in valid:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)

        # Prefer resources we can grab at least as fast, especially when few remain.
        lead = od - sd
        value = lead * 3.0 + (1.5 if sd <= 1 else 0.0) - sd * (0.15 if not few else 0.35)

        # Centrality tie-break to reduce pathing.
        cc = abs(rx - cx) + abs(ry - cy)
        value -= cc * (0.03 if not few else 0.01)

        # If both are far, slightly prefer closer to opponent when it doesn't harm lead.
        if sd > 3 and od > 3:
            value += (od - sd) * 0.2

        if value > best_val:
            best_val = value
            best = (rx, ry)

    rx, ry = best
    dx = 0
    dy = 0
    if rx > sx:
        dx = 1
    elif rx < sx:
        dx = -1
    if ry > sy:
        dy = 1
    elif ry < sy:
        dy = -1
    return [dx, dy]