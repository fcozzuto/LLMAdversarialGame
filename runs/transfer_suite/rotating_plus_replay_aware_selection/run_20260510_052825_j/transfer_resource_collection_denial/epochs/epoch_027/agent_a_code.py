def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obstacles_list}

    def man(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    valid = []
    for r in resources:
        x, y = r[0], r[1]
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    tr = observation.get("turns_remaining", 0)
    remaining = observation.get("remaining_resource_count", len(valid))
    few = tr <= 5 or remaining <= 3

    best = None
    best_key = None
    for rx, ry in valid:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        margin = od - sd  # positive means we are closer
        center_bias = - (abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))
        if few:
            value = (-sd * 1.4) + (margin * 1.0) + center_bias * 0.05
        else:
            value = (margin * 2.2) + (-sd * 0.35) + (center_bias * 0.08)
        if sd <= 1:
            value += 3.0
        # Deterministic tie-break: higher value, then smaller sd, then lexicographic (rx,ry)
        key = (value, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]