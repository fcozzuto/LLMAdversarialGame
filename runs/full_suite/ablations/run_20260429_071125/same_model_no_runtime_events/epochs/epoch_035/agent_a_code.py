def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best = [0, 0]
    if resources:
        tx, ty = resources[0]
        bestd = dist(sx, sy, tx, ty)
        for rx, ry in resources[1:]:
            d = dist(sx, sy, rx, ry)
            if d < bestd:
                bestd, tx, ty = d, rx, ry
        cur = dist(sx, sy, tx, ty)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                nd = dist(nx, ny, tx, ty)
                if nd < cur or (nd == cur and (dx, dy) < (best[0], best[1])):
                    cur, best = nd, [dx, dy]
        return best

    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = 0
        if resources is not None:
            score += -dist(nx, ny, ox, oy)  # prefer moving away from opponent
        score += -dist(nx, ny, (w - 1) // 2, (h - 1) // 2)  # prefer center
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < (best[0], best[1])):
            best_score = score
            best = [dx, dy]
    return best