def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    target = None
    bestd = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        d = cheb(sx, sy, rx, ry)
        if bestd is None or d < bestd or (d == bestd and (rx + ry) < (target[0] + target[1])):
            bestd = d
            target = (rx, ry)

    if target is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = target

    candidates = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist_to = cheb(nx, ny, tx, ty)
        dist_from_opp = cheb(nx, ny, ox, oy)
        score = (-dist_to, dist_from_opp, -(nx + ny))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move