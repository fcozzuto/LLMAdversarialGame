def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))

    if res:
        tx, ty = min(res, key=lambda c: (abs(c[0] - sx) + abs(c[1] - sy), c[0], c[1]))
    else:
        tx, ty = ox, oy

    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dist = abs(nx - tx) + abs(ny - ty)
        # Prefer approaching target; also slightly avoid moving closer to opponent when no resources.
        opp_bonus = 0
        if not res:
            opp_bonus = abs(nx - ox) + abs(ny - oy)
        val = (dist, -opp_bonus, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]