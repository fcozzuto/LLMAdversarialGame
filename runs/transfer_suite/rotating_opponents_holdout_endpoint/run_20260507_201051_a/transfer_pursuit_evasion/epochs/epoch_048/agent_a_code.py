def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Deterministic target: nearest resource; if none, a corner farthest from opponent.
    if res:
        tx, ty = min(res, key=lambda r: (dist2(sx, sy, r[0], r[1]), r[0], r[1]))
        primary = lambda x, y: dist2(x, y, tx, ty)
        maximize_opponent = False
    else:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (dist2(c[0], c[1], ox, oy), -c[0], -c[1]))
        primary = lambda x, y: dist2(x, y, tx, ty)
        maximize_opponent = True

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dprim = primary(nx, ny)
        dop = dist2(nx, ny, ox, oy) if maximize_opponent else -dist2(nx, ny, ox, oy)
        # Tie-break deterministically to avoid oscillation
        key = (dprim, -dop, nx, ny) if not maximize_opponent else (dprim, dop, nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]