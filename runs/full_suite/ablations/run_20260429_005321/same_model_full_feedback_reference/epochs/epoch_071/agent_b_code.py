def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if not resources:
        # Deterministic center drift with obstacle avoidance
        best = (10**18, 0, 0)  # (d2 to center, dx, dy) minimal
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d2c = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            cand = (int(d2c * 1000), dx, dy)
            if cand < best:
                best = cand
        return [best[1], best[2]]

    # Target choice: prefer resources closer to us than opponent, with a bias to deny opponent.
    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best_tx, best_ty = resources[0]
    best_key = None
    for x, y in resources:
        myd = d2(sx, sy, x, y)
        opd = d2(ox, oy, x, y)
        # Lower key is better: prioritize smaller (myd - 0.7*opd), then closer to center for tie-break.
        key = (myd - int(0.7 * opd), d2(x, y, cx, cy), x, y)
        if best_key is None or key < best_key:
            best_key = key
            best_tx, best_ty = x, y

    tx, ty = best_tx, best_ty

    # Move choice: decrease our distance to target; if tied, increase opponent distance to that target.
    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = d2(nx, ny, tx, ty)
        # slight center attraction to reduce dithering when close
        center_bias = d2(nx, ny, cx, cy)
        opd = d2(ox, oy, tx, ty)
        score = (myd, center_bias, -opd, dx, dy)  # lexicographic min
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]