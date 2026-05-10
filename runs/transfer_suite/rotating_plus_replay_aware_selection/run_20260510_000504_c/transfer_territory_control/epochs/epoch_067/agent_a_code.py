def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    target = None
    if resources:
        tx, ty = resources[0]
        bestd = manh(sx, sy, tx, ty)
        for x, y in resources[1:]:
            d = manh(sx, sy, x, y)
            if d < bestd or (d == bestd and (x, y) < (tx, ty)):
                bestd = d
                tx, ty = x, y
        target = (tx, ty)
    if target is None and unclaimed:
        tx, ty = sorted(unclaimed)[0]
        target = (tx, ty)

    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0
        if target is not None:
            v += -manh(nx, ny, target[0], target[1]) * 10
        else:
            v += -manh(nx, ny, cx, cy)
        d_opp = manh(nx, ny, ox, oy)
        v += d_opp * 2
        if (nx, ny) in unclaimed:
            v += 6
        if v > bestv or (v == bestv and (dx, dy) < (best[0], best[1])):
            bestv = v
            best = [dx, dy]
    return best