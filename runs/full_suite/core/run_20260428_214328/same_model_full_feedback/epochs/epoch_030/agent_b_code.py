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

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = [(abs(dx) + abs(dy), dx, dy) for dx, dy in moves]
    dirs.sort(key=lambda t: (t[0], t[1], t[2]))

    best = None
    best_score = -10**18

    if resources:
        res_sorted = sorted(resources, key=lambda r: dist2(sx, sy, r[0], r[1]))
        targets = res_sorted[:5]
    else:
        targets = []

    for _, dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = 0
        if targets:
            score += -min(dist2(nx, ny, tx, ty) for tx, ty in targets)
        else:
            score += -dist2(nx, ny, ox, oy)
        score += -dist2(nx, ny, ox, oy) * 0.2
        score += (nx == ox and ny == oy) * 1000000
        if score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]