def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for b in (observation.get("obstacles") or []):
        if isinstance(b, (list, tuple)) and len(b) >= 2:
            x, y = int(b[0]), int(b[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # If invalid/blocked current position, fallback to staying.
    if (sx, sy) in obs:
        return [0, 0]

    # Greedy pursuit with obstacle-aware tie-breaking.
    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dxx, dyy = nx - ox, ny - oy
        dist2 = dxx * dxx + dyy * dyy
        # Penalize moves that aim "through" adjacent obstacles by discouraging stepping next to walls.
        adj_pen = 0
        for ax, ay in ((nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1), (nx + 1, ny + 1), (nx + 1, ny - 1), (nx - 1, ny + 1), (nx - 1, ny - 1)):
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obs:
                adj_pen += 3
        # Prefer moving closer on either axis; discourage staying unless it’s the only option.
        axis_pref = 0
        if dx == 0 and dy == 0:
            axis_pref = 6
        else:
            axis_pref = (0 if (abs(nx - ox) + abs(ny - oy)) < (abs(sx - ox) + abs(sy - oy)) else 2)
        score = dist2 + adj_pen + axis_pref
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]