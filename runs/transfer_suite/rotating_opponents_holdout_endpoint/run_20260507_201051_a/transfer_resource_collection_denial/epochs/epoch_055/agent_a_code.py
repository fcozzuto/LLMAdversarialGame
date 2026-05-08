def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def sgn(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    best = None
    best_score = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        score = do - ds  # prefer where we are closer than opponent
        key = (-score, ds, rx, ry) if best is None else None
        if best is None or (score > best_score) or (score == best_score and (ds, rx, ry) < (best[0], best[1], best[2])):
            best = (ds, rx, ry)
            best_score = score

    _, tx, ty = best
    dx = sgn(tx - sx)
    dy = sgn(ty - sy)

    dirs = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    seen = set()
    for mx, my in dirs:
        if (mx, my) in seen:
            continue
        seen.add((mx, my))
        nx, ny = sx + mx, sy + my
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [mx, my]
    return [0, 0]