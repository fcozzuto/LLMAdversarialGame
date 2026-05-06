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

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not res:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            key = (-(nx + ny), man((nx, ny), (w - 1, h - 1)))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    cur_target = min(res, key=lambda r: man((sx, sy), r))
    best_overall = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        self_d = man((nx, ny), cur_target)
        opp_d = man((nx, ny), (ox, oy))
        best_target_score = None
        for rx, ry in res:
            sd = man((nx, ny), (rx, ry))
            od = man((ox, oy), (rx, ry))
            # Prefer resources where we are closer than opponent, but still keep moving toward them.
            s = (od - sd) * 10 - sd
            # Slightly discourage drifting away from opponent while chasing
            s -= (0 if sd == 0 else (sd > self_d) * 2)
            if best_target_score is None or s > best_target_score:
                best_target_score = s
        # If scores tie, prefer increasing x+y (toward top-right for our start), then closer to a current target.
        tie_key = (-best_target_score, -(nx + ny), man((nx, ny), cur_target), man((nx, ny), (ox, oy)))
        if best_overall is None or tie_key < best_overall[0]:
            best_overall = (tie_key, dx, dy)

    return [best_overall[1], best_overall[2]] if best_overall else [0, 0]