def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                v = md(nx, ny, ox, oy)
                if v > bestv:
                    bestv = v
                    best = (dx, dy)
        return [best[0], best[1]]

    # Interceptor-style: pick a move that maximizes earliest advantage to some target resource
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate best target resource under "can I arrive before opponent?"
        local_best = -10**18
        for rx, ry in resources:
            ts = md(nx, ny, rx, ry)
            to = md(ox, oy, rx, ry)
            # Prefer resources where we can beat opponent soon; tie-break by closer arrival
            v = (to - ts) * 1000 - ts
            if v > local_best:
                local_best = v
        # Small tie-break toward staying aligned with opponent sweep potential (same row/col)
        sweep_bonus = 0
        if ny == oy:
            sweep_bonus += 5
        if nx == ox:
            sweep_bonus += 3

        v = local_best + sweep_bonus
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]