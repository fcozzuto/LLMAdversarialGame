def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) and ("pursuer" not in role)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        if isinstance(it, dict):
            x, y = it.get("x"), it.get("y")
        else:
            x, y = it[0], it[1]
        try:
            x, y = int(x), int(y)
        except Exception:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        sx = max(0, min(w - 1, sx))
        sy = max(0, min(h - 1, sy))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_opp = man(nx, ny, ox, oy)
        # Secondary term: discourage getting boxed in; prefer increasing available moves for evader, decreasing for pursuer
        avail = 0
        for ddx, ddy in deltas:
            tx, ty = nx + ddx, ny + ddy
            if ok(tx, ty):
                avail += 1
        if is_evader:
            toward_corner = -man(nx, ny, far_corner[0], far_corner[1])
            score = (d_opp * 2.0) + (toward_corner * 0.7) + (avail * 0.1)
        else:
            toward_corner = -man(nx, ny, far_corner[0], far_corner[1])
            score = (-d_opp * 2.0) + (toward_corner * 0.05) + (-avail * 0.08)
        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]