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

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def heuristic(from_pos, target):
        fx, fy = from_pos
        tx, ty = target
        self_d = cheb((fx, fy), (tx, ty))
        opp_d = cheb((ox, oy), (tx, ty))
        row_bias = abs(ty - oy)  # contest resources near opponent's current sweep band
        return self_d - 1.15 * opp_d + 0.35 * row_bias

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not res:
        # deterministic "drift" to reduce being swept off resources: go toward center row band
        center_row = h // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            val = abs(ny - center_row) + 0.02 * abs(nx - (w // 2))
            if val < best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # pick the best target under relative closeness + band contest
    best_target = None
    best_val = 10**18
    for t in res:
        v = heuristic((sx, sy), t)
        if v < best_val:
            best_val = v
            best_target = t

    # choose one-step move that best improves heuristic toward that target
    tx, ty = best_target
    best = (10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        v = heuristic((nx, ny), (tx, ty))
        # slight preference to reduce distance directly (deterministic tie-break)
        v2 = v * 100 + cheb((nx, ny), (tx, ty))
        if v2 < best[0]:
            best = (v2, dx, dy)
    return [best[1], best[2]]