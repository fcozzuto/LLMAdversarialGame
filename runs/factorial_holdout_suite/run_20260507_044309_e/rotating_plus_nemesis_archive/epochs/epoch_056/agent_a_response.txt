def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    my_corner = min(corners, key=lambda c: abs(sx - c[0]) + abs(sy - c[1]))
    def md(x, y, tx, ty): return abs(x - tx) + abs(y - ty)

    best = None
    best_key = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        opp_adv = od - sd  # positive: we are closer
        corner_prog = -md(rx, ry, my_corner[0], my_corner[1])
        # Encourage taking resources we're likely to reach before opponent; slight preference for closer total.
        key = (opp_adv * 100 - sd + corner_prog, opp_adv, -sd, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    if (sx + dx, sy) in obstacles and (sx, sy + dy) in obstacles:
        return [0, 0]
    if (sx + dx, sy) in obstacles:
        dx = 0
    if (sx, sy + dy) in obstacles:
        dy = 0

    return [int(dx), int(dy)]