def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    target = None
    if res:
        bestd = None
        for x, y in res:
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            if bestd is None or d < bestd:
                bestd = d
                target = (x, y)
    else:
        target = (cx, cy)

    best_score = None
    best_move = (0, 0)
    tx, ty = target

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        d_to_t = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        center_pen = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        score = (-d_to_t) + 0.35 * d_opp - 0.05 * center_pen
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]