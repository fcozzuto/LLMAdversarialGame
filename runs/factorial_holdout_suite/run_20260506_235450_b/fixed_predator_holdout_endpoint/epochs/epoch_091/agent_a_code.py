def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def ti(v):
        try:
            return int(v)
        except:
            return 0

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = ti(sp[0]), ti(sp[1])
    ox, oy = ti(op[0]), ti(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = ti(p[0]), ti(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    cells = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = ti(r[0]), ti(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                cells.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    if not cells:
        if valid(sx, sy):
            return [0, 0]
        for dx, dy in moves:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    best = None
    for x, y in cells:
        d = abs(x - sx) + abs(y - sy)
        if best is None or (d, x, y) < best:
            best = (d, x, y)
    tx, ty = best[1], best[2]

    curd = abs(tx - sx) + abs(ty - sy)
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        stop = 1 if (dx == 0 and dy == 0) else 0
        away_op = abs(tx - nx) + abs(ty - ny) - (abs(tx - ox) + abs(ty - oy))
        scored.append((nd, stop, -away_op, dx, dy, nd - curd))
    if not scored:
        return [0, 0]
    scored.sort()
    return [scored[0][3], scored[0][4]]