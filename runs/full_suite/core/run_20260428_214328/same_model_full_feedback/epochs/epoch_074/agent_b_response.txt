def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Pick a resource we can "race" better than opponent (using Manhattan race heuristic)
    if resources:
        best_res = None
        best_val = -10**18
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Prefer resources with large (opponent advantage over us negative -> we win)
            val = (opd - myd) * 10 - myd
            # Mild tie-break toward staying closer to board center (deterministic)
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            val -= int(0.5 * (abs(rx - cx) + abs(ry - cy)))
            if val > best_val:
                best_val = val
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        tx, ty = (w - 1 - ox, h - 1 - oy)  # fallback: head to opponent- opposite-like corner

    # Choose move that minimizes our distance to target, but keeps "race lead" pressure and advances toward opponent
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)
        race = (opd - myd) * 10 - myd
        # Advance toward opponent corner (diagonal bias)
        adv = (md(nx, ny, w - 1, h - 1) * -1) + (md(nx, ny, 0, 0) * 0)
        score = race + adv
        # Deterministic tie-break: prefer lexicographically smaller delta among equals
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]