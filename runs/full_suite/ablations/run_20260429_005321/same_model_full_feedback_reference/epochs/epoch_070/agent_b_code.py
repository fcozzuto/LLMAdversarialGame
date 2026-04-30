def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if resources:
        tx, ty = resources[0]
        best = (sx - tx) * (sx - tx) + (sy - ty) * (sy - ty)
        for x, y in resources[1:]:
            d = (sx - x) * (sx - x) + (sy - y) * (sy - y)
            if d < best:
                best, tx, ty = d, x, y
    else:
        tx, ty = cx, cy

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_self = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        d_opp = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        # Prefer getting closer to target; tie-break by staying farther from opponent.
        val = -d_self * 1000 + d_opp
        if val > best_val:
            best_val, best_move = val, (dx, dy)
    return [int(best_move[0]), int(best_move[1])]