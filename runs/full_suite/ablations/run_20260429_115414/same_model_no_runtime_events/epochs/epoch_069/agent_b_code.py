def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

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
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    best = None
    best_score = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        diff = od - sd  # positive => we can arrive sooner
        # Prefer clearly winnable targets; otherwise reduce our distance and increase opponent distance.
        score = (diff, -sd, od, -abs(rx - (w - 1) / 2.0) - abs(ry - (h - 1) / 2.0))
        if best_score is None or score > best_score:
            best_score = score
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    candidates = []
    for mx in (dx, 0, -dx):
        for my in (dy, 0, -dy):
            if mx == 0 and my == 0 and (dx != 0 or dy != 0):
                pass
            nx, ny = sx + mx, sy + my
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((cheb(nx, ny, rx, ry), cheb(nx, ny, ox, oy), nx - sx, ny - sy))
    if not candidates:
        return [0, 0]

    # Minimize our distance to target; then maximize distance from opponent.
    candidates.sort(key=lambda t: (t[0], -t[1], t[2], t[3]))
    _, _, mdx, mdy = candidates[0]
    return [int(mdx), int(mdy)]