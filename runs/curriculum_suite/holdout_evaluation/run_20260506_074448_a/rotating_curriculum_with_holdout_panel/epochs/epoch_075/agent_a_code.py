def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate move by best resource we can contest/claim next.
        move_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            oppd = man(ox, oy, rx, ry)
            # Prefer resources where we are earlier, and also prefer ones closer in absolute terms.
            tempo = oppd - myd  # higher => we arrive first
            cent = -(abs(rx - cx) + abs(ry - cy))
            reach = -myd
            # If opponent is closer (tempo<0), still allow moving toward them but with reduced weight.
            key = (-tempo if tempo < 0 else 0, -tempo, -myd, cent)
            # Use a deterministic aggregate across resources by taking the maximum tempo/benefit.
            cand = (tempo, reach + 0.01 * cent, -myd, rx, ry, key)
            if move_best is None or cand > move_best:
                move_best = cand

        # If all resources blocked (unlikely), stay
        if move_best is None:
            continue

        # Prefer non-still moves slightly to ensure progress.
        progress = 0.001 if (dx != 0 or dy != 0) else 0.0
        overall = (move_best[0] + progress, move_best[1], move_best[2], dx, dy)
        if best is None or overall > best:
            best = overall

    if best is None:
        return [0, 0]
    return [best[3], best[4]]