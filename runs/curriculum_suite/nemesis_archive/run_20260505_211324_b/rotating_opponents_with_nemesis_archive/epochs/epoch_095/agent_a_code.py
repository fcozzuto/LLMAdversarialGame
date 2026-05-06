def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not res:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [dx, dy]
        return [0, 0]

    best_t = None
    best_sc = None
    for tx, ty in res:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        sc = ds - int(do * 12 / 10)  # prefer resources where we are significantly closer
        if best_sc is None or sc < best_sc or (sc == best_sc and (ds < md(sx, sy, best_t[0], best_t[1]) if best_t else True)):
            best_sc = sc
            best_t = (tx, ty)

    tx, ty = best_t
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = md(nx, ny, tx, ty)
        opp_dist = md(ox, oy, tx, ty)
        # If opponent is likely to take the target, reduce their distance too (more contesting).
        contest = dist + (0 if ds <= opp_dist else 1)
        key = (contest, dist, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]