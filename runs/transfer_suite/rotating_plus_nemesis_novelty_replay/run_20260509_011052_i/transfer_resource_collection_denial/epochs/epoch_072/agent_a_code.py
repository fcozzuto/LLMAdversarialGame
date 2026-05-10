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
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_key = None
    for rx, ry in resources:
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Primary: be closer than opponent; Secondary: smaller self distance;
        # Tertiary: smaller opp distance; Quaternary: deterministic tie break by coordinates.
        advantage = opp_d - self_d  # positive => we are closer
        key = (
            advantage,
            -self_d,
            -opp_d,
            -abs(rx - sx) - abs(ry - sy),
            -rx,
            -ry,
        )
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (dx != 0 or dy != 0) and (nx, ny) in blocked:
        # Try axis alternative if diagonal hits obstacle; else stay.
        if dx != 0 and (sx + dx, sy) not in blocked:
            return [dx, 0]
        if dy != 0 and (sx, sy + dy) not in blocked:
            return [0, dy]
        return [0, 0]
    return [dx, dy]