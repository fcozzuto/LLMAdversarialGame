def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    role_self = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role_self) or ("pursuer" not in role_self and "hunter" not in role_self and "chaser" not in role_self)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        a = dx if dx >= 0 else -dx
        b = dy if dy >= 0 else -dy
        m = a if a >= b else b
        return m * m

    if is_evader:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        far_corner = max(corners, key=lambda c: cheb2(c[0], c[1], ox, oy))
        tx, ty = far_corner
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = cheb2(nx, ny, ox, oy)
            corner_pull = -cheb2(nx, ny, tx, ty)
            key = (dist, corner_pull, -((nx == sx and ny == sy) * 1))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # pursuer: minimize distance to opponent with obstacle-aware tie-breaks
    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb2(nx, ny, ox, oy)
        on_line = -abs(nx - ox) - abs(ny - oy)  # closer in L1 helps also
        key = (-dist, on_line, -((nx == sx and ny == sy) * 1))
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    return list(best if best is not None else (0, 0))