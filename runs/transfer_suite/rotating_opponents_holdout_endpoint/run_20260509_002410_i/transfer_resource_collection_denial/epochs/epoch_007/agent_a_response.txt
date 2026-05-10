def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]
    obstacle_set = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y, w, h):
        return 0 <= x < w and 0 <= y < h

    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    best = None  # (key, tx, ty)
    for rx, ry in resources:
        if (rx, ry) in obstacle_set:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds
        # tie-break: prefer resources slightly "offset" to avoid row-sweep collisions
        offset_bias = -abs((rx - sx) - (ry - sy))
        # prefer smaller ds if equal lead
        key = (lead, offset_bias, -ds, -do, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    if best is None:
        return [0, 0]
    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    def step_eval(nx, ny):
        if not inside(nx, ny, w, h) or (nx, ny) in obstacle_set:
            return (-10**9, 10**9, 10**9, 0)
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        lead = no - ns
        return (lead, -ns, -abs(tx - nx) - abs(ty - ny), 0)

    candidates = []
    # prioritize direct move then alternatives around it, deterministic order
    candidates.append((dx, dy))
    for ddx in (-1, 0, 1):
        for ddy in (-1, 0, 1):
            if (ddx, ddy) != (dx, dy):
                if abs(ddx) <= 1 and abs(ddy) <= 1:
                    candidates.append((ddx, ddy))
    # keep stay included
    if (0, 0) not in candidates:
        candidates.append((0, 0))

    best_step = (0, 0)
    best_val = None
    for ddx, ddy in candidates:
        nx, ny = sx + ddx, sy + ddy
        val = step_eval(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_step = (ddx, ddy)

    return [int(best_step[0]), int(best_step[1])]