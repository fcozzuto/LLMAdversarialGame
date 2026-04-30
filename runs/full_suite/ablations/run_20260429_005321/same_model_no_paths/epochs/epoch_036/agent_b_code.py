def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    tx, ty = (w // 2, h // 2)
    if resources:
        best = None
        bestd = 10**18
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd or (d == bestd and (x, y) < best):
                bestd = d
                best = (x, y)
        tx, ty = best

    # If opponent is closer to the target, drift to the next-best target (deterministic).
    if resources:
        o_bestd = 10**18
        for x, y in resources:
            d = abs(x - ox) + abs(y - oy)
            if d < o_bestd:
                o_bestd = d
        myd = abs(tx - sx) + abs(ty - sy)
        if o_bestd < myd:
            best = None
            bests = 10**18
            for x, y in resources:
                s = abs(x - sx) + abs(y - sy) - 2 * (abs(x - ox) + abs(y - oy) == o_bestd)
                if s < bests or (s == bests and (x, y) < best):
                    bests = s
                    best = (x, y)
            if best is not None:
                tx, ty = best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = -(abs(tx - nx) + abs(ty - ny))
        val -= 1 if (nx, ny) == (ox, oy) else 0
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]