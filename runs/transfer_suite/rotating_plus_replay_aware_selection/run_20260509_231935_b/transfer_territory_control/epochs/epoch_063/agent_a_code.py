def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set(tuple(p) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def legal(x, y):
        return inside(x, y) and (x, y) not in obs
    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    unclaimed = observation.get("unclaimed_cells") or []
    targets = []
    if unclaimed:
        for p in unclaimed:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                x, y = int(p[0]), int(p[1])
                if legal(x, y):
                    targets.append((x, y))
    if not targets:
        targets = [(ox, oy)]

    def score_cell(x, y):
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        edge = 1 if (x == 0 or y == 0 or x == w - 1 or y == h - 1) else 0
        return ds * 2 - do + edge * -0.5

    best_t = None
    best_sc = None
    for x, y in targets:
        sc = score_cell(x, y)
        if best_sc is None or sc < best_sc or (sc == best_sc and (x, y) < best_t):
            best_sc = sc
            best_t = (x, y)

    tx, ty = best_t
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = man(nx, ny, tx, ty) * 10 - man(nx, ny, ox, oy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]