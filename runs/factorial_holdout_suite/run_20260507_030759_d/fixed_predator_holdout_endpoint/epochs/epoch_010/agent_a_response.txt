def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def steps(a, b, c, d):
        ax, ay = a, b
        bx, by = c, d
        return max(abs(bx - ax), abs(by - ay))

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            d = steps(nx, ny, tx, ty)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    prefer_ahead = []
    for rx, ry in resources:
        ds = steps(sx, sy, rx, ry)
        do = steps(ox, oy, rx, ry)
        prefer_ahead.append((ds <= do, ds - do, ds + do, rx, ry))
    ahead = [r for r in prefer_ahead if r[0]]
    cand = ahead if ahead else prefer_ahead
    cand.sort(key=lambda z: (z[0] is False, z[1], z[2]))  # deterministic

    best_move = None
    best_val = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        # Evaluate best resource for this step; tie-break by lower our distance, then lower opponent lead.
        local = None
        for _, _, _, rx, ry in cand[:6]:
            ds2 = steps(nx, ny, rx, ry)
            do2 = steps(ox, oy, rx, ry)
            val = (ds2 - do2, ds2, do2, rx, ry)
            if local is None or val < local[0]:
                local = (val, rx, ry)
        val = local[0]
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]