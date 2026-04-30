def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    if resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            mind = None
            for rx, ry in resources:
                d = abs(nx - rx) if abs(nx - rx) > abs(ny - ry) else abs(ny - ry)
                if mind is None or d < mind:
                    mind = d
            if best is None or mind < best[0] or (mind == best[0] and (dx, dy) < best[1]):
                best = (mind, (dx, dy))
        return [best[1][0], best[1][1]]

    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])
    bestd = None
    bestm = (0, 0)
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = abs(nx - ox) if abs(nx - ox) > abs(ny - oy) else abs(ny - oy)
        if bestd is None or d < bestd or (d == bestd and (dx, dy) < bestm):
            bestd = d
            bestm = (dx, dy)
    return [bestm[0], bestm[1]]