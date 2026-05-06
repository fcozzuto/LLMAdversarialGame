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

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    # Heuristic target selection: prioritize resources that are comparatively faster for us
    # and penalize cells on/near opponent sweep rows.
    if res:
        best = None
        best_key = None
        for rx, ry in res:
            sd = cheb((sx, sy), (rx, ry))
            od = cheb((ox, oy), (rx, ry))
            row_pen = 0
            if ry == oy:
                row_pen += 6
            if abs(ry - oy) == 1:
                row_pen += 2
            col_pen = 0
            if rx == ox:
                col_pen += 2
            if abs(rx - ox) == 1:
                col_pen += 1
            key = (od - sd - row_pen - col_pen, -sd, (rx, ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w // 2), (h // 2)

    # Choose a move that reduces distance to the target; break ties by increasing separation from opponent.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_to_t = cheb((nx, ny), (tx, ty))
        d_sep = cheb((nx, ny), (ox, oy))
        row_block = 0
        if ty == oy and ny == oy:
            row_block = 3
        score = (-d_to_t, d_sep + row_block, (nx, ny))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move