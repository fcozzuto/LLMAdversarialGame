def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if resources:
        best = resources[0]
        bd = dist(sx, sy, best[0], best[1])
        for r in resources[1:]:
            d = dist(sx, sy, r[0], r[1])
            if d < bd or (d == bd and (r[0], r[1]) < best):
                best, bd = r, d
        tx, ty = best
    else:
        tx, ty = (w // 2, h // 2)

    curd = dist(sx, sy, tx, ty)
    best_move = [0, 0]
    bestd = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist(nx, ny, tx, ty)
        if d < bestd or (d == bestd and (dx, dy) < (best_move[0], best_move[1])):
            bestd = d
            best_move = [dx, dy]

    if bestd == 10**9:
        return [0, 0]
    return best_move