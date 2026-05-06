def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0] or 0), int(sp[1] or 0)
    ox, oy = int(op[0] or 0), int(op[1] or 0)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if not p or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if not r or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))

    def dist(a, b, c, d):
        ax = a - c
        if ax < 0:
            ax = -ax
        by = b - d
        if by < 0:
            by = -by
        return ax + by

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def score_target(x, y):
        ds = dist(sx, sy, x, y)
        do = dist(ox, oy, x, y)
        return ds - do * 2

    if res:
        best_x, best_y = res[0]
        best = score_target(best_x, best_y)
        for x, y in res[1:]:
            s = score_target(x, y)
            if s < best or (s == best and (x + y) < (best_x + best_y)):
                best = s
                best_x, best_y = x, y
        tx, ty = best_x, best_y
    else:
        # Move toward center while keeping away from opponent
        tx, ty = (w - 1) // 2, (h - 1) // 2
        if dist(sx, sy, ox, oy) <= 2:
            if ox == sx:
                ty = 0 if oy > sy else (h - 1)
            elif oy == sy:
                tx = 0 if ox > sx else (w - 1)

    dxs = [-1, 0, 1]
    dys = [-1, 0, 1]
    moves = []
    for dx in dxs:
        for dy in dys:
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        # Try staying in place if surrounded (should rarely happen; still valid fallback)
        return [0, 0]

    # One-step greedy: minimize distance to target, but prefer moves not too close to opponent
    best_move = moves[0]
    best_val = 10**18
    for dx, dy, nx, ny in moves:
        dtx = dist(nx, ny, tx, ty)
        dox = dist(nx, ny, ox, oy)
        val = dtx - 0.3 * dox
        if val < best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]