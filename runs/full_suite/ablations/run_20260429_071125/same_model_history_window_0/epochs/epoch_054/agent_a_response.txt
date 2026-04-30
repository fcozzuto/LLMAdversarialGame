def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):  # Chebyshev for movement with diagonals
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def better_target():
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            key = (max(ds - do, 0), ds, rx, ry)  # prefer where we aren't worse, then closer, then stable tie
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return best[1] if best else None

    target = better_target()
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if target is None:
        # fallback: head toward center
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        target = (int(round(tx)), int(round(ty)))

    tx, ty = target
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        d_after = dist((nx, ny), (tx, ty))
        # small preference to move toward target direction deterministically
        toward = (1 if (dx == 0 and dy == 0) else 0)  # 0 if moving
        key = (d_after, toward, nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]