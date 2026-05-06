def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if w <= 0 or h <= 0:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    # Target: nearest resource when available, else center.
    if resources:
        target = min(resources, key=lambda t: (abs(t[0] - sx) + abs(t[1] - sy), abs(t[0] - ox) + abs(t[1] - oy), t[0], t[1]))
    else:
        target = (w // 2, h // 2)

    # If opponent is very close, reduce risk by increasing distance more aggressively.
    close = (abs(sx - ox) + abs(sy - oy)) <= 2
    opp_weight = 1.8 if close else 0.9

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obst:
            continue

        dres = abs(nx - target[0]) + abs(ny - target[1])
        dop = abs(nx - ox) + abs(ny - oy)

        # Mild preference to keep moving (avoid being stuck against obstacles).
        corner_bias = 0
        if resources:
            # Prefer progress along target direction deterministically.
            corner_bias = 0.15 * (-(dres) + abs(nx - target[0]) + abs(ny - target[1]) - dres)

        # Additional obstacle proximity penalty to reduce bumping patterns.
        near_obst = 0
        for tx, ty in ((nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1), (nx + 1, ny + 1), (nx + 1, ny - 1), (nx - 1, ny + 1), (nx - 1, ny - 1)):
            if (tx, ty) in obst:
                near_obst += 1
        obst_pen = 0.6 * near_obst

        # Deterministic tie-breaker: lexicographic on move.
        val = (-1.2 * dres) + (opp_weight * dop) + corner_bias - obst_pen + (0.01 if (dx, dy) == (0, 0) else 0.0)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]