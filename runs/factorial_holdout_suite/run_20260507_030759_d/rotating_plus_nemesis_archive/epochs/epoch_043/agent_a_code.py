def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    if not res or (sx, sy) in obst:
        return [0, 0]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for diagonal moves

    # Limit candidate targets deterministically: closest few by self distance now
    scored_res = []
    for tx, ty in res:
        sd = dist(sx, sy, tx, ty)
        od = dist(ox, oy, tx, ty)
        # prefer resources that self can reach not later than opponent, otherwise still consider
        advantage = od - sd
        key = (advantage + 1000) * 1000000 - sd * 1000 - (tx + ty)
        scored_res.append((key, sd, od, tx, ty))
    scored_res.sort(key=lambda z: z[0])
    targets = [(t[3], t[4]) for t in scored_res[:6]]

    best_move = (0, 0)
    best_val = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                nx, ny = sx, sy
            else:
                nx, ny = sx + dx, sy + dy
                if nx < 0: nx = 0
                if nx >= w: nx = w - 1
                if ny < 0: ny = 0
                if ny >= h: ny = h - 1
            if (nx, ny) in obst:
                continue

            # Choose best target according to "can I secure it sooner?"
            local_best = None
            for tx, ty in targets:
                nsd = dist(nx, ny, tx, ty)
                nod = dist(ox, oy, tx, ty)
                # strong bias to securing before opponent; deterministic tie-break
                val = (nod - nsd) * 1000000 - nsd * 10 - (tx * 8 + ty)
                if local_best is None or val > local_best:
                    local_best = val
            if local_best is None:
                continue
            if best_val is None or local_best > best_val:
                best_val = local_best
                best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]