def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    resources = observation.get("resources", []) or []
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    tr = int(observation.get("remaining_resource_count", 999) or 999)
    endgame = tr <= 5

    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        x, y = int(r[0]), int(r[1])
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        lead = od - sd
        # Key: secure earlier (lead), then closeness; in endgame, prioritize absolute closeness.
        key = (sd if endgame else -sd, -lead, sd, od)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    if best is None:
        return [0, 0]

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]