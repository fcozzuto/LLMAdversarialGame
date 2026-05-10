def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = (observation.get("self_role") or "").lower()
    pursuer = "pursuer" in role

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    bestv = None

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def edge_dist(x, y):
        return min(x, y, w - 1 - x, h - 1 - y)

    def obs_penalty(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in blocked:
                    p += 1
        return p

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        man = abs(nx - ox) + abs(ny - oy)
        cheb = max(abs(nx - ox), abs(ny - oy))
        ed = edge_dist(nx, ny)
        op_adj = 1 if (abs(nx - ox) <= 1 and abs(ny - oy) <= 1) else 0
        pen = obs_penalty(nx, ny)

        if pursuer:
            # Chase: minimize distance; avoid adjacency-to-obstacles only mildly.
            v = - (10 * man + 3 * cheb + 2 * pen + 6 * op_adj - ed)
        else:
            # Evade: maximize distance; prefer center when threatened; avoid obstacle adjacency.
            threatened = 1 if (abs(sx - ox) + abs(sy - oy) <= 4) else 0
            v = (12 * man + 4 * cheb + 2 * ed - (5 * threatened) - 4 * pen - (3 * op_adj))

        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]