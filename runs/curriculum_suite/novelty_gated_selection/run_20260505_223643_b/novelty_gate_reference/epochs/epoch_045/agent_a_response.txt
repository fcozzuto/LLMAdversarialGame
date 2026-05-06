def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0] or 0), int(sp[1] or 0)
    ox, oy = int(op[0] or 0), int(op[1] or 0)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        cx, cy = w // 2, h // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    def md(a, b, c, d):
        x = a - c
        if x < 0: x = -x
        y = b - d
        if y < 0: y = -y
        return x + y

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine would keep us; mirror deterministically

        # Evaluate by best "swing" on the most favorable contested resource.
        # Swing > 0 means we are closer than opponent to that resource.
        local_best = -10**9
        for tx, ty in resources:
            myd = md(nx, ny, tx, ty)
            opd = md(ox, oy, tx, ty)
            val = (opd - myd) * 10 - myd  # prefer securing/contesting and not falling behind
            if val > local_best:
                local_best = val

        # Tie-break: prefer moves that reduce our distance to nearest resource.
        if local_best == local_best:  # keep deterministic path
            nearest_after = min(md(nx, ny, tx, ty) for tx, ty in resources)
            nearest_now = min(md(sx, sy, tx, ty) for tx, ty in resources)
            penalty = 0 if nearest_after <= nearest_now else (nearest_after - nearest_now) * 2
            val2 = local_best - penalty
        else:
            val2 = local_best

        if best_val is None or val2 > best_val or (val2 == best_val and (dx, dy) < best_move):
            best_val = val2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]