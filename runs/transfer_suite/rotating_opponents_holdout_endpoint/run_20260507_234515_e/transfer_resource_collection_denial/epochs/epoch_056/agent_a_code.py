def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid_resources = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                valid_resources.append((x, y))

    if not valid_resources:
        best_dxdy = None
        best_val = None
        for dx, dy, nx, ny in cand:
            # Prefer moving away from opponent to reduce denial pressure.
            val = (man(nx, ny, ox, oy), -man(nx, ny, sx, sy), -dx, -dy)
            if best_val is None or val > best_val:
                best_val = val
                best_dxdy = (dx, dy)
        return [best_dxdy[0], best_dxdy[1]]

    best = None
    for dx, dy, nx, ny in cand:
        # Evaluate best target this move can reach while accounting for opponent.
        local_best = None
        for rx, ry in valid_resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            # Bonus if we are closer than opponent; penalty if we are likely to lose.
            val = (opd - myd) * 10 - myd + (1 if (nx == rx and ny == ry) else 0)
            # Small tie-break: favor targets toward which we move.
            val -= 0.01 * (abs(rx - sx) + abs(ry - sy))
            if local_best is None or val > local_best:
                local_best = val
        # Risk aversion near obstacles: prefer positions with more free neighbors.
        free_n = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                tx, ty = nx + adx, ny + ady
                if inb(tx, ty):
                    free_n += 1
        score = (local_best, free_n, -(man(nx, ny, ox, oy)))
        if best is None or score > best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]