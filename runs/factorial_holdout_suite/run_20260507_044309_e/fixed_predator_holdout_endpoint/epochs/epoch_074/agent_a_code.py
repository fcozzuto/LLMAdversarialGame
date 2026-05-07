def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    # Heuristic: pick a move that maximizes "resource advantage" over opponent,
    # while steering away from obstacles and map edges.
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    dirs = [d for d in dirs if not (d[0] == 0 and d[1] == 0)] + [(0, 0)]

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    def adj_obst(x, y):
        c = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = x + ddx, y + ddy
                if (nx, ny) in obstacles:
                    c += 1
        return c

    # Precompute best target score per cell-like closeness using Chebyshev distance (diagonal-friendly).
    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Edge penalty encourages central movement to keep options.
        edge_pen = (0 if nx != 0 else 2) + (0 if nx != w - 1 else 2) + (0 if ny != 0 else 2) + (0 if ny != h - 1 else 2)
        obst_pen = adj_obst(nx, ny)

        # Choose the single resource that yields the best advantage after this move.
        local_best = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; tie-break to larger lead, then shorter self distance.
            val = (od - sd, -sd)
            if local_best is None or val > local_best:
                local_best = val
        # Combine: primary from resource advantage, then obstacle/edge penalties.
        total = (local_best[0] * 10 - obst_pen - edge_pen, local_best[1])
        if best_val is None or total > best_val:
            best_val = total
            best = [dx, dy]

    return best if best is not None else [0, 0]