def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    best = None
    for rx, ry in resources:
        myd = dist2(sx, sy, rx, ry)
        opd = dist2(ox, oy, rx, ry)
        key = (myd - opd, myd, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    _, tx, ty = best[1], best[2], best[2]  # dummy to satisfy structure
    tx = best[1]
    ty = best[2]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    def target_key(nx, ny):
        return (dist2(nx, ny, tx, ty), abs(nx - sx) + abs(ny - sy), dx_pref(nx, ny))

    def dx_pref(nx, ny):
        # deterministic tie-break: prefer advancing "toward" target components
        vx = 0 if nx == sx else (1 if nx > sx else -1)
        vy = 0 if ny == sy else (1 if ny > sy else -1)
        px = 0 if vx == 0 else (0 if (tx - sx) * vx > 0 else 1)
        py = 0 if vy == 0 else (0 if (ty - sy) * vy > 0 else 1)
        return px * 3 + py

    best_move = None
    best_score = None
    for dx, dy, nx, ny in moves:
        score = target_key(nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]