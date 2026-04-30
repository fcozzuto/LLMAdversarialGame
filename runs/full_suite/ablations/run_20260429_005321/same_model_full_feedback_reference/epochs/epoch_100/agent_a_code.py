def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        tx, ty = min(resources, key=lambda r: (dist(sx, sy, r[0], r[1]), r[0], r[1]))
        best, bestv = (0, 0), -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -dist(nx, ny, tx, ty) * 10
            v += dist(nx, ny, ox, oy)  # prefer moving away from opponent slightly
            if (dx, dy) == (0, 0):
                v -= 1  # discourage standing still
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [int(best[0]), int(best[1])]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best, bestv = (0, 0), -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = -dist(nx, ny, cx, cy)
        v += dist(nx, ny, ox, oy) * 0.5
        if (dx, dy) == (0, 0):
            v -= 1
        if v > bestv:
            bestv, best = v, (dx, dy)
    return [int(best[0]), int(best[1])]