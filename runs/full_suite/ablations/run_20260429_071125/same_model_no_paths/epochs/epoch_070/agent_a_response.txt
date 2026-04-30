def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # If current cell is blocked (shouldn't happen), stay.
    if (sx, sy) in blocked:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Goal: minimize distance to best resource from candidate next cell, with obstacle/edge risk penalties.
    if resources:
        res_list = resources
    else:
        # Move toward center when no resources visible.
        res_list = [((w - 1) / 2.0, (h - 1) / 2.0)]

    best_move = (0, 0)
    best_cost = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Resource distance (chebyshev makes diagonal preference).
        dmin = 10**9
        for rx, ry in res_list:
            cd = cheb(nx, ny, rx, ry)
            if cd < dmin:
                dmin = cd

        # Obstacle risk: if many adjacent blocked cells, add penalty (prevents getting trapped).
        adj_blocked = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if not (0 <= tx < w and 0 <= ty < h) or (tx, ty) in blocked:
                    adj_blocked += 1

        # Mild preference to avoid staying still when movement can reduce distance.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0

        # Tie-breaker deterministic: fixed ordering via cost tuple.
        cost_tuple = (dmin * 10 + adj_blocked * 2 + stay_pen, dx, dy)
        if best_cost is None or cost_tuple < best_cost:
            best_cost = cost_tuple
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]