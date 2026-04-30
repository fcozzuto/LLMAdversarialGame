def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        if ok(sx + dx, sy + dy):
            moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            bestd = 10**9
            for rx, ry in resources:
                d = abs(nx - rx)
                e = abs(ny - ry)
                dd = d if d > e else e
                if dd < bestd:
                    bestd = dd
            # smaller distance to resources is better; slight bias toward moving
            score = (-bestd, -abs(dx) - abs(dy))
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # No visible resources: move away from opponent
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        dd = abs(nx - ox)
        e = abs(ny - oy)
        dist = dd if dd > e else e
        # prefer increasing distance, tie-break by moving
        score = (dist, -abs(dx) - abs(dy))
        if best is None or score > best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]