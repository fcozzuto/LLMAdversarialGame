def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for p in obstacles:
        try:
            blocked.add((p[0], p[1]))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    if resources:
        best = None
        best_key = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            # Score higher is better: prefer being closer than opponent to the best resource.
            my_best = 10**9
            op_best = 10**9
            for rx, ry in resources:
                d1 = md(nx, ny, rx, ry)
                d2 = md(ox, oy, rx, ry)
                if d1 < my_best:
                    my_best = d1
                if d2 < op_best:
                    op_best = d2
            # Also prefer moving toward center for tie-break.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center = - (abs(nx - cx) + abs(ny - cy))
            key = (op_best - my_best, center, -md(nx, ny, ox, oy))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources visible: maximize distance from opponent, tie-break by center.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = legal[0]
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        key = (md(nx, ny, ox, oy), -(abs(nx - cx) + abs(ny - cy)), -(dx == 0 and dy == 0))
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)
    return [best[0], best[1]]