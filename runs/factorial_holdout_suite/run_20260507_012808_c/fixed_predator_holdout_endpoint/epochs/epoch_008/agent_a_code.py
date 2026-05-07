def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            d = abs(nx - cx) + abs(ny - cy)
            cand = (d, nx, ny)
            if best is None or cand < best:
                best = cand
        return [best[1] - sx, best[2] - sy]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        best_for = None
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # higher is better: we arrive closer than opponent
            # Prefer immediate pickup, then maximize advantage, then minimize our distance
            cand = (adv, -1 if (nx == rx and ny == ry) else 0, -sd)
            if best_for is None or cand > best_for:
                best_for = cand
        # Secondary tie-break: keep away from obstacles isn't needed; use closer to best resource
        # Compute our distance to nearest resource from candidate.
        nd = min(man(nx, ny, rx, ry) for rx, ry in resources)
        overall = (best_for[0], best_for[1], best_for[2], -nd, nx, ny)
        if best is None or overall > best:
            best = overall

    return [best[4] - sx, best[5] - sy]