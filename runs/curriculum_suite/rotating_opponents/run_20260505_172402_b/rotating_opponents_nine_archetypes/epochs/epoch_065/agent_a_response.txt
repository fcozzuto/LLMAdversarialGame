def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d_self = abs(nx - tx) + abs(ny - ty)
            d_opp = abs(nx - ox) + abs(ny - oy)
            val = (-d_opp, d_self)
            if best is None or val < best[0]:
                best = (val, [dx, dy])
        return best[1] if best else [0, 0]

    best_res = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer targets where we can get there sooner; tie-break by smaller ds then farther from opponent
        key = (ds - do, ds, -do)
        if best_res is None or key < best_res[0]:
            best_res = (key, (rx, ry))
    rx, ry = best_res[1]

    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_self = cheb(nx, ny, rx, ry)
        d_opp = cheb(nx, ny, ox, oy)
        # primary: reduce distance to target; secondary: keep away from opponent; tertiary: avoid staying
        val = (d_self, -d_opp, abs(nx - sx) + abs(ny - sy))
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move if best_val is not None else [0, 0]