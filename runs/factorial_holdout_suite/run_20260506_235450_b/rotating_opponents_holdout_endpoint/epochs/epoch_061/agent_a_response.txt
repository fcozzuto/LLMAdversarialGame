def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    ap = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for a in observation.get("obstacles") or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        else:
            try:
                x, y = int(a.get("x")), int(a.get("y"))
            except Exception:
                continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        else:
            try:
                x, y = int(r.get("x")), int(r.get("y"))
            except Exception:
                continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            res.append((x, y))

    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def eval_at(px, py):
        best = None
        best_m = -10**9
        for x, y in res:
            sd = cheb(px, py, x, y)
            od = cheb(ox, oy, x, y)
            m = od - sd
            if m > best_m:
                best_m = m
                best = (x, y, sd, od)
            elif m == best_m and best is not None and sd < best[2]:
                best = (x, y, sd, od)
        return best_m, best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = None

    _, best = eval_at(sx, sy)
    tx, ty = (best[0], best[1]) if best else (sx, sy)

    # Try immediate improvement first toward best target; then choose best one-step safe move.
    preferred = []
    dx1 = 0 if tx == sx else (1 if tx > sx else -1)
    dy1 = 0 if ty == sy else (1 if ty > sy else -1)
    preferred.append((dx1, dy1))
    preferred += [m for m in moves if m != (dx1, dy1)]

    for dx, dy in preferred:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        mval, _ = eval_at(nx, ny)
        # tie-break: prefer shorter self distance to chosen target
        t_sd = cheb(nx, ny, tx, ty)
        cur = (mval, -t_sd)
        if best_val is None or cur > best_val:
            best_val = cur
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]