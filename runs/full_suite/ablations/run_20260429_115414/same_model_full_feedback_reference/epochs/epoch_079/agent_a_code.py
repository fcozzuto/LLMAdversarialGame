def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    if not resources:
        cx, cy = (W - 1) // 2, (H - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = dist(nx, ny, cx, cy)
            cand = (-d, dx, dy)
            if best is None or cand > best:
                best = cand
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    best_score = -10**18
    best_move = [0, 0]
    # deterministic ordering tie-break by move order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_min = 10**9
        best_rel = -10**9
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            if myd < my_min:
                my_min = myd
            rel = opd - myd
            if rel > best_rel:
                best_rel = rel
        # Prefer moves that improve relative advantage, then approach best resource.
        # Also slightly prefer staying closer to opponent-front (reduce opponent advantage).
        after_opd_min = 10**9
        for rx, ry in resources:
            d = dist(ox, oy, rx, ry)
            if d < after_opd_min:
                after_opd_min = d
        score = best_rel * 1000 - my_min * 10 - after_opd_min * 0.1
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move