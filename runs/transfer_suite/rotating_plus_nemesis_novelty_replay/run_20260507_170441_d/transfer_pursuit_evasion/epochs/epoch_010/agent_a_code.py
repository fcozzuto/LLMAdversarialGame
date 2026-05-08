def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                res.append((rx, ry))

    sr = (observation.get("self_role", "") or "").lower()
    orl = (observation.get("opponent_role", "") or "").lower()
    pursuer = ("purs" in sr) or ("tag" in sr) or ("chase" in sr) or (("evad" in orl) and ("evad" not in sr))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    def dist2(x, y, u, v):
        dx = x - u
        dy = y - v
        return dx * dx + dy * dy

    def block_penalty(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    pen += 1
        return pen

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if res:
            d = min(dist2(nx, ny, rx, ry) for rx, ry in res)
            val = d + 3 * block_penalty(nx, ny)
        else:
            d_op = dist2(nx, ny, ox, oy)
            val = (-d_op if pursuer else d_op) + 2 * block_penalty(nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move