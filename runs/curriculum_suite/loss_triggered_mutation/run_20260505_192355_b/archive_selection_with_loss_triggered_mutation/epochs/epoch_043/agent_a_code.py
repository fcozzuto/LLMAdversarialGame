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

    if not res:
        best = (0, 0)
        bestd = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            if d > bestd or (d == bestd and (dx, dy) < best):
                bestd, best = d, (dx, dy)
        return [best[0], best[1]]

    target = res[0]
    best = 10**9
    for x, y in res:
        d = abs(x - sx) + abs(y - sy)
        if d < best or (d == best and (x, y) < target):
            best = d
            target = (x, y)

    tx, ty = target
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            nd = abs(tx - nx) + abs(ty - ny)
            cd = abs(tx - ox) + abs(ty - oy)
            score = -nd
            if abs(nx - ox) + abs(ny - oy) <= abs(sx - ox) + abs(sy - oy):
                score -= 1 if (cd <= best) else 0
            cand.append((score, nd, dx, dy))
    cand.sort(reverse=True, key=lambda t: (t[0], -t[1], -t[2], -t[3]))
    if not cand:
        return [0, 0]
    return [int(cand[0][2]), int(cand[0][3])]