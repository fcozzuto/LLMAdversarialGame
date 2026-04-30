def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not inb(sx, sy):
        return [0, 0]

    if any((sx, sy) == r for r in res):
        return [0, 0]

    legal = [(sx + dx, sy + dy, dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    best = None
    best_score = -10**9
    for nx, ny, dx, dy in legal:
        dist_to_res = 10**6
        if res:
            for rx, ry in res:
                d = cheb(nx, ny, rx, ry)
                if d < dist_to_res:
                    dist_to_res = d
        dist_to_op = cheb(nx, ny, ox, oy)
        score = -dist_to_res * 10 + dist_to_op
        if (nx, ny) == (ox, oy):
            score -= 50
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]