def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def dist_cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not res:
        return [0, 0]

    # Counter sweep: bias toward resources on/near opponent row, and toward targets we can reach sooner.
    best_t = None
    best_sc = None
    for rx, ry in res:
        sd = dist_cheb((sx, sy), (rx, ry))
        od = dist_cheb((ox, oy), (rx, ry))
        row_bias = 2 if ry == oy else (1 if abs(ry - oy) <= 1 else 0)
        col_bias = 1 if rx == ox else 0
        sc = (od - sd) * 10 + row_bias * 3 + col_bias * 2 - sd
        if best_sc is None or sc > best_sc or (sc == best_sc and sd < best_t[2]):
            best_t = (rx, ry, sd)
            best_sc = sc

    tx, ty, _ = best_t

    # Choose best legal move one step toward (with fallback if blocked)
    vx = 0 if tx == sx else (1 if tx > sx else -1)
    vy = 0 if ty == sy else (1 if ty > sy else -1)
    pref = (vx, vy)

    def move_score(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            return -10**9
        sd = dist_cheb((nx, ny), (tx, ty))
        # If stepping toward is impossible, still prefer reducing opponent's reach to contested row targets
        row_contest = 2 if ty == oy else (1 if abs(ty - oy) <= 1 else 0)
        return -sd + row_contest

    best_mv = (0, 0)
    best_ms = -10**9
    # Try pref first, then remaining moves deterministically
    order = [pref] + [m for m in moves if m != pref]
    for dx, dy in order:
        ms = move_score(dx, dy)
        if ms > best_ms:
            best_ms = ms
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]