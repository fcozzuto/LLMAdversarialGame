def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        gap = od - sd
        key = (gap, -sd, -(rx + ry), -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    _, tx, ty = best[0], best[1], best[2]

    # Choose among all 8 neighbors + stay, deterministically by distance-to-target then move order.
    cand = []
    move_order = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        d = man(nx, ny, tx, ty)
        cand.append((d, 0 if (dx, dy) == (0, 0) else 1, -dx, -dy, dx, dy))
    if not cand:
        return [0, 0]
    cand.sort()
    _, _, _, _, dx, dy = cand[0]
    return [int(dx), int(dy)]