def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in (observation.get("obstacles") or []):
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
        elif isinstance(a, dict) and "x" in a and "y" in a:
            x, y = int(a["x"]), int(a["y"])
        else:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = int(r["x"]), int(r["y"])
        else:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    if not resources:
        return [0, 0]

    def d(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonal steps)

    opp = (ox, oy)
    me = (sx, sy)

    best = None
    best_key = None
    for x, y in resources:
        r = (x, y)
        sd = d(me, r)
        od = d(opp, r)
        margin = od - sd  # >0 means we are faster
        # Heuristic: if opponent is already closer, deprioritize; otherwise, also prefer nearer resources.
        # Tie-break: prefer resources that are not directly "in the same sweep line" as opponent.
        line_pen = 0
        if oy == y:  # opponent could sweep along this row
            line_pen += 1
        if ox == x:  # opponent could sweep along this column (diagonal/row sweep variant)
            line_pen += 1
        key = (margin - 0.05 * line_pen, -sd, x, y)
        if best_key is None or key > best_key:
            best_key = key
            best = r

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    if dx == 0 and dy == 0:
        return [0, 0]

    return [dx, dy]