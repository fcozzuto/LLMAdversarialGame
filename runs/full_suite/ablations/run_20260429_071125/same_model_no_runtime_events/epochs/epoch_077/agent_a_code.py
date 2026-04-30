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

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def moves_9():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                yield dx, dy

    # Choose target resource with deterministic "relative closeness" preference
    best = None
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        rel = d_op - d_me  # positive => I'm closer
        # Prefer resources I can beat, otherwise still pick best relative
        key = (0 if d_me <= d_op else 1, -rel, d_me, (rx, ry))
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Score immediate moves by progress toward target and safety
    opts = []
    for dx, dy in moves_9():
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d1 = cheb(nx, ny, tx, ty)
        d0 = cheb(sx, sy, tx, ty)
        # Prefer getting closer; discourage moving adjacent to opponent
        opp_adj = (abs((sx + dx) - ox) <= 1 and abs((sy + dy) - oy) <= 1)
        center_bias = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2) * 1e-3
        step_reward = (d0 - d1) * 10.0
        obst_adj = 0
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                if ix == 0 and iy == 0:
                    continue
                if (nx + ix, ny + iy) in obstacles:
                    obst_adj += 1
        key = (1 if opp_adj else 0, d1, -step_reward, obst_adj, -(center_bias), dx, dy)
        opts.append((key, [dx, dy]))
    if not opts:
        return [0, 0]
    opts.sort(key=lambda t: t[0])
    return opts[0][1]