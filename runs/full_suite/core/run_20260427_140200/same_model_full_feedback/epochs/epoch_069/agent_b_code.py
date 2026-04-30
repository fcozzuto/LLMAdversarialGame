def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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
        targets = [(ox, oy)]
    else:
        targets = resources

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    bestd = 10**9
    for tx, ty in targets:
        d = cheb(sx, sy, tx, ty)
        if d < bestd:
            bestd = d
            best = (tx, ty)

    tx, ty = best if best is not None else (ox, oy)
    best_move = (0, 0)
    best_score = 10**9

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        score = d
        if (nx, ny) == (ox, oy):
            score -= 1
        if (nx, ny) in targets:
            score -= 2
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if not (-1 <= dx <= 1 and -1 <= dy <= 1) or dx != int(dx) or dy != int(dy):
        return [0, 0]
    return [int(dx), int(dy)]