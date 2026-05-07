def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    if not res:
        tx, ty = w // 2, h // 2
    else:
        best = None
        for x, y in res:
            myd = md(sx, sy, x, y)
            opd = md(ox, oy, x, y)
            lead = myd - opd  # want <=0 (me earlier)
            score = (lead, myd, x, y)
            if best is None or score < best[0]:
                best = (score, x, y)
        tx, ty = best[1], best[2]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    desired = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, 0), (0, -dy)]
    # add alternate diagonal variations deterministically
    desired += [(dx, -dy), (-dx, dy), (-dx, -dy), (dx, 1 if dy == 0 else 0), (1 if dx == 0 else 0, dy)]

    for adx, ady in desired:
        nx, ny = sx + int(adx), sy + int(ady)
        if inb(nx, ny):
            return [int(adx), int(ady)]

    # fallback: stay still
    return [0, 0]