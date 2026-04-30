def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    targets = resources if resources else [(ox, oy)]
    tx, ty = min(targets, key=lambda t: cheb(sx, sy, t[0], t[1]))

    best = None
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = cheb(nx, ny, tx, ty)
            if resources:
                score += 0.01 * ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
            else:
                score += 0.01 * ((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty))
            if best is None or score < best_score or (score == best_score and (dx, dy) < best):
                best = (dx, dy)
                best_score = score

    if best is None:
        return [0, 0]
    return [best[0], best[1]]