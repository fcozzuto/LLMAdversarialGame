def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)

    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = sp[0], sp[1] if isinstance(sp, (list, tuple)) and len(sp) >= 2 else (0, 0)
    ox, oy = op[0], op[1] if isinstance(op, (list, tuple)) and len(op) >= 2 else (0, 0)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    res_pts = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]
    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obs

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if res_pts:
        tx, ty = min(res_pts, key=lambda r: (man(sx, sy, r[0], r[1]), r[0], r[1]))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(0, 0)]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            moves.append((dx, dy))

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = man(nx, ny, tx, ty)
        opp_dist = man(nx, ny, ox, oy)
        key = (dist, -opp_dist, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2]]]