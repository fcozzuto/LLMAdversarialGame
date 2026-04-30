def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_adj(x, y):
        c = 0
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                if ix == 0 and iy == 0:
                    continue
                if (x + ix, y + iy) in obstacles:
                    c += 1
        return c

    best = None
    best_key = None
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        ahead = d2 - d1  # positive if we are closer
        # Prefer blocking: when equal distance, slightly prefer lower opponent distance
        # and also penalize obstacle adjacency near the target.
        key = (-(ahead), d1, obst_adj(rx, ry), (rx + ry) % 3, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Check candidate moves (including staying) and pick best that moves toward target.
    candidates = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, 0), (0, -dy), (-dx, -dy), (dx, -dy), (-dx, dy)]
    cand_best = None
    cand_key = None
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer smaller distance to target; if tie, prefer larger distance from opponent.
        key = (d_to, -d_opp, obst_adj(nx, ny), (nx + ny) % 2)
        if cand_key is None or key < cand_key:
            cand_key = key
            cand_best = (mx, my)

    return [int(cand_best[0]), int(cand_best[1])]