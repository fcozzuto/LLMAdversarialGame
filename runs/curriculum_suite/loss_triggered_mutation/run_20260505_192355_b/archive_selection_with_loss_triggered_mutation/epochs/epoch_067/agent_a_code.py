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

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    # New strategy: race/deny based on arrival time advantage over opponent.
    # Prefer resources where we can arrive no later than opponent; tie-break by larger lead, then nearer.
    for rx, ry in res:
        d_me = dist((sx, sy), (rx, ry))
        d_opp = dist((ox, oy), (rx, ry))
        arrive_diff = d_opp - d_me  # positive => we are earlier
        key = (0 if arrive_diff >= 0 else 1, -arrive_diff, d_me, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Move to reduce Chebyshev distance to chosen target; if blocked, try alternative deterministic.
    best_move = (None, None)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_now = dist((sx, sy), (tx, ty))
        d_next = dist((nx, ny), (tx, ty))
        # Prefer strict improvement; tie-break by proximity to target, then by move vector.
        imp = 1 if d_next < d_now else 0
        key = (-imp, d_next, dx, dy)
        if best_move[0] is None or key < best_move[0]:
            best_move = (key, [dx, dy])
    if best_move[1] is not None:
        return best_move[1]

    return [0, 0]