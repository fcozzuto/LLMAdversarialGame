def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if resources:
        best = None
        bestd = 10**9
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd or (d == bestd and (x, y) < best):
                bestd = d
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = int((w - 1) / 2), int((h - 1) / 2)

    prefers_away = abs(ox - sx) + abs(oy - sy) <= 2
    score_moves = []
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if prefers_away:
            val = abs(nx - ox) + abs(ny - oy)
        else:
            val = - (abs(nx - tx) + abs(ny - ty))
        if (nx, ny) in resources:
            val += 1000
        score_moves.append((val, dx, dy))

    if not score_moves:
        if inb(sx, sy):
            return [0, 0]
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    score_moves.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, dx, dy = score_moves[0]
    return [int(dx), int(dy)]