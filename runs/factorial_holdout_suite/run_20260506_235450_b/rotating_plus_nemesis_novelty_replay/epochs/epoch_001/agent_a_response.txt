def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            val = dist2(nx, ny, tx, ty)
            key = (val, abs(nx - ox) + abs(ny - oy), nx, ny)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    best_res = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = dist2(sx, sy, rx, ry)
        od = dist2(ox, oy, rx, ry)
        # Prefer resources we're at least competitive for; tie-break deterministically.
        val = (sd - (od // 4), sd, od, rx, ry)
        if best_res is None or val < best_res[0]:
            best_res = (val, (rx, ry))
    _, (tx, ty) = best_res

    best = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Primary: reduce distance to chosen target.
        d1 = dist2(nx, ny, tx, ty)
        # Secondary: don't step into a cell that's better for opponent on that target.
        d_op = dist2(ox, oy, tx, ty)
        # Tertiary: slightly prefer moves that improve relative race.
        rel = (d1 - (d_op // 4))
        key = (rel, d1, abs(nx - tx) + abs(ny - ty), nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1] if best else [0, 0]