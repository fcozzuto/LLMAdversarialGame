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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None

    if resources:
        target = None
        bestd = None
        for rx, ry in resources:
            d = cheb(sx, sy, rx, ry)
            if bestd is None or d < bestd or (d == bestd and (rx, ry) < target):
                bestd = d
                target = (rx, ry)
        tx, ty = target
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # small bias to reduce distance to opponent if tied (keeps deterministic)
            bias = cheb(nx, ny, ox, oy) * 0.01
            score = d + bias
            if best_score is None or score < best_score or (score == best_score and (nx, ny) < best):
                best_score = score
                best = (nx, ny, dx, dy)
        if best is not None:
            return [best[2], best[3]]

    # fallback: head toward quadrant containing opponent or center
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    ax = ox if resources else cx
    ay = oy if resources else cy
    tx = 1 if sx < ax else (-1 if sx > ax else 0)
    ty = 1 if sy < ay else (-1 if sy > ay else 0)
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            candidates.append((cheb(nx, ny, ax, ay), nx, ny, dx, dy))
    candidates.sort(key=lambda t: (t[0], t[1], t[2]))
    return [candidates[0][3], candidates[0][4]] if candidates else [0, 0]