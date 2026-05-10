def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    # Filter valid resources not on obstacles (if any)
    valid = []
    for r in resources:
        x, y = r[0], r[1]
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    tr = observation.get("turns_remaining", 0)
    few = tr <= 5 or observation.get("remaining_resource_count", len(valid)) <= 3

    best = None
    for rx, ry in valid:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer cells we can reach sooner than opponent; when few left, prioritize nearest to us.
        margin = od - sd
        value = margin * 2.0 - sd * 0.6 + (0.15 if few else 0.0) * (-sd)
        # If we are already adjacent, prioritize grabbing quickly.
        if sd <= 1:
            value += 2.5
        # Light tie-break toward central to reduce pathing collisions.
        cx = (rx - (w - 1) / 2)
        cy = (ry - (h - 1) / 2)
        value -= 0.01 * (cx * cx + cy * cy)
        cand = (value, -sd, rx, ry)
        if best is None or cand > best:
            best = cand

    _, _, tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If moving directly would step into obstacle, fall back to axis-wise move.
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Try moving x only, then y only, else stay; deterministic order.
        ax = 0 if tx == sx else (1 if tx > sx else -1)
        ay = 0 if ty == sy else (1 if ty > sy else -1)
        if (sx + ax, sy) not in obstacles and ax != 0:
            dx, dy = ax, 0
        elif (sx, sy + ay) not in obstacles and ay != 0:
            dx, dy = 0, ay
        else:
            dx, dy = 0, 0

    return [int(dx), int(dy)]