def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evader = ("evader" in self_role) or ("pursuer" in self_role and "evader" in opp_role)

    resources = observation.get("resources") or []
    res = []
    for it in resources:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not inb(sx, sy):
        sx, sy = max(0, min(w - 1, sx)), max(0, min(h - 1, sy))
        if (sx, sy) in obstacles:
            for dx, dy in moves:
                if inb(sx + dx, sy + dy):
                    sx, sy = sx + dx, sy + dy
                    break

    if (sx, sy) == (ox, oy):
        return [0, 0]

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    # Target: closest resource to current position (deterministic)
    tx, ty = sx, sy
    if res:
        best = None
        for x, y in res:
            d = man(sx, sy, x, y)
            key = (d, x, y)
            if best is None or key < best[0]:
                best = (key, x, y)
        tx, ty = best[1], best[2]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        opp_d = man(nx, ny, ox, oy)
        res_d = man(nx, ny, tx, ty) if res else 0
        if evader:
            score = opp_d * 100 - res_d
        else