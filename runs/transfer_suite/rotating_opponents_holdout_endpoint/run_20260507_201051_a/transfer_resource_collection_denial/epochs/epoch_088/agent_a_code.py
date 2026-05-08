def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w); h = int(h)
    except:
        w = 8; h = 8
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (w - 1, h - 1))
    sx, sy = sp if isinstance(sp, (list, tuple)) and len(sp) >= 2 else (0, 0)
    ox, oy = op if isinstance(op, (list, tuple)) and len(op) >= 2 else (w - 1, h - 1)
    try:
        sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)
    except:
        sx = 0; sy = 0; ox = w - 1; oy = h - 1

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            try:
                x = int(x); y = int(y)
            except:
                continue
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            try:
                x = int(x); y = int(y)
            except:
                continue
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        tx, ty = resources[0]
        bestd = man(sx, sy, tx, ty)
        for rx, ry in resources[1:]:
            d = man(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                tx, ty = rx, ry
        targetx, targety = tx, ty
    else:
        targetx, targety = ox, oy

    best = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_t = man(nx, ny, targetx, targety)
        d_to_o = man(nx, ny, ox, oy)
        d_step = man(nx, ny, sx, sy)
        cand = (d_to_t, d_to_o, d_step, dx, dy)
        if cand < best:
            best = cand

    if best[3] == 0 and best[4] == 0:
        return [0, 0]
    return [int(best[3]), int(best[4])]