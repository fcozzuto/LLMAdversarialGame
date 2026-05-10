def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def best_target(points):
        if not points:
            return None
        best = None
        bestd = 10**18
        for p in points:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if not inb(x, y):
                    continue
                d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
                if d < bestd:
                    bestd = d
                    best = (x, y)
        return best

    target = best_target(observation.get("resources") or [])
    if target is None:
        target = best_target(observation.get("unclaimed_cells") or [])

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    cur_dop = (sx - ox) * (sx - ox) + (sy - oy) * (sy - oy)
    avoid = cur_dop <= 9

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dop = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        if avoid:
            score = dop
        else:
            if target is not None:
                tx, ty = target
                dt = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
                score = -dt
            else:
                cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
                dc = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
                score = -dc
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]