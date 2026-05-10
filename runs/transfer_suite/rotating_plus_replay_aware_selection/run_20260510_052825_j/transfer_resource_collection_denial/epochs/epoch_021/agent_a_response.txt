def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    valid = []
    for r in resources:
        x, y = r[0], r[1]
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            valid.append((x, y))
    if not valid:
        return [0, 0]

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    tr = observation.get("turns_remaining", 0)
    remaining_count = observation.get("remaining_resource_count", len(valid))
    few = tr <= 5 or remaining_count <= 3

    best = None
    for rx, ry in valid:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        margin = od - sd  # higher means we are closer than opponent
        # Core: win contest for next resource; secondary: encourage closeness when few remain
        value = margin * 3.0 - sd * (0.6 if not few else 1.0) + (2.0 if sd <= 1 else 0.0)
        # Small deterministic tie-break toward our preferred quadrant (helps reduce dithering)
        center_bias = -0.01 * (abs(rx - (w // 2)) + abs(ry - (h // 2)))
        value += center_bias
        key = (value, -sd, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))

    tx, ty = best[1]
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]