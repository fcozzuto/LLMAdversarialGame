def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        tx, ty = ox, oy
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_key = None
    best_t = resources[0]

    for x, y in resources:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Prefer resources we can reach strictly earlier; then maximize margin; then nearer.
        margin = od - sd
        # Slightly prefer central/lower-risk targets to reduce ties deterministically.
        center_bias = -((x - (w - 1) / 2.0) ** 2 + (y - (h - 1) / 2.0) ** 2)
        key = (1 if margin > 0 else 0, margin, -sd, center_bias)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (x, y)

    tx, ty = best_t
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in blocked or not (0 <= nx < w and 0 <= ny < h):
        # Deterministic local detour: try axis-aligned first, then diagonal, then stay.
        options = []
        options.append((1 if tx > sx else -1 if tx < sx else 0, 0))
        options.append((0, 1 if ty > sy else -1 if ty < sy else 0))
        options.append((dx, dy))
        options.append((0, 0))
        for ddx, ddy in options:
            cx, cy = sx + ddx, sy + ddy
            if 0 <= cx < w and 0 <= cy < h and (cx, cy) not in blocked:
                return [int(ddx), int(ddy)]
        return [0, 0]

    return [int(dx), int(dy)]