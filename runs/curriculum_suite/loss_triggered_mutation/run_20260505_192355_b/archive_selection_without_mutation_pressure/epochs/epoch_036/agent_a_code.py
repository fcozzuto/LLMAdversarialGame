def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    raw_res = observation.get("resources") or []
    resources = []
    for r in raw_res:
        if isinstance(r, dict):
            x = r.get("x", r.get(0, None))
            y = r.get("y", r.get(1, None))
        else:
            x, y = r[0], r[1]
        if x is None or y is None:
            continue
        resources.append((int(x), int(y)))

    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_move = [0, 0]
    best_val = -10**18
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        val = -10**18
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            if myd == 0:
                score = 10**9
            else:
                score = (opd - myd) * 100 - myd * 2
                if opd == myd:
                    score -= 3
            cx_bias = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)) * 0.001
            score += cx_bias
            if score > val:
                val = score
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move