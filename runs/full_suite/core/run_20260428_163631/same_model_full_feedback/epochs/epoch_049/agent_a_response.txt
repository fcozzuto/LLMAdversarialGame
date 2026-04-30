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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target race strategy: prefer resources we can reach sooner than opponent.
    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            score = (do - ds) * 10 - ds  # maximize winning margin, then shorter
            if best is None or score > best_score or (score == best_score and (ds, rx, ry) < (cheb(sx, sy, best[0], best[1]), best[0], best[1])):
                best = (rx, ry)
                best_score = score
        tx, ty = best
    else:
        tx, ty = (w - 1 if sx <= (w - 1) // 2 else 0), (h - 1 if sy <= (h - 1) // 2 else 0)

    # Obstacle-safe greedy step: minimize distance-to-target; break ties by maximizing opponent distance.
    chosen = (0, 0)
    best1 = None
    best2 = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dself = cheb(nx, ny, tx, ty)
        dop = cheb(ox, oy, tx, ty)
        # Prefer smaller dself; if tie, prefer farther from opponent's target pressure (i.e., larger dop - dself)
        val1 = dself
        val2 = (dop - dself)
        if best1 is None or val1 < best1 or (val1 == best1 and val2 > best2):
            best1 = val1
            best2 = val2
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]