def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    valid_moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    if not res:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        for x, y in res:
            if (sx, sy) == (x, y):
                continue
            ours = d2(sx, sy, x, y)
            opp = d2(ox, oy, x, y)
            key = (ours - opp, ours, x, y)
            if best is None or key < best[0]:
                best = (key, (x, y))
        tx, ty = best[1] if best is not None else res[0]

    best_move = (0, 0)
    best = None
    for dx, dy in valid_moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
            dx, dy = 0, 0
        ours = d2(nx, ny, tx, ty)
        opp = d2(ox, oy, tx, ty)
        key = (ours - opp, ours, abs(nx - tx) + abs(ny - ty), nx, ny, dx, dy)
        if best is None or key < best:
            best = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]