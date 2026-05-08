def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if not ok(sx, sy):
        sx, sy = 0, 0
        if not ok(sx, sy):
            return [0, 0]

    dirs = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_score = None

    rx = ry = None
    res = observation.get("resources") or []
    if res and isinstance(res, list):
        rp = res[0]
        if isinstance(rp, (list, tuple)) and len(rp) >= 2:
            rx, ry = int(rp[0]), int(rp[1])

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = -abs(ox - nx) - abs(oy - ny)
        if rx is not None and 0 <= rx < w and 0 <= ry < h and ok(rx, ry):
            score += 0.05 * (-abs(rx - nx) - abs(ry - ny))
        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [best[0], best[1]]