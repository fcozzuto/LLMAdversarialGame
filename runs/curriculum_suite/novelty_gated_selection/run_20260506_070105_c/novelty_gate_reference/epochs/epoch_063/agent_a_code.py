def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    # Sweep-row opponent: contest resources on/opposite to their current y first,
    # otherwise take tempo advantage with a mild far-target penalty.
    best = None
    best_score = -10**18
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        tempo = (do - ds)  # positive means we are closer
        row_bonus = 0
        if ry == oy:
            row_bonus += 6
        if ry == oy + 1 or ry == oy - 1:
            row_bonus += 2
        col_bonus = 0
        if rx == ox:
            col_bonus += 2
        far_pen = (ds + do) * 0.02
        score = tempo * 10 + row_bonus + col_bonus - far_pen
        if score > best_score:
            best_score = score
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # Deterministically try alternative axis approach to avoid obstacle.
        cand = [(-dx, dy), (dx, -dy), (0, dy), (dx, 0), (0, 0)]
        for ddx, ddy in cand:
            cx, cy = sx + ddx, sy + ddy
            if 0 <= cx < w and 0 <= cy < h and (cx, cy) not in obstacles:
                return [int(ddx), int(ddy)]
        return [0, 0]
    return [int(dx), int(dy)]