def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        d0 = a[0] - b[0]
        if d0 < 0: d0 = -d0
        d1 = a[1] - b[1]
        if d1 < 0: d1 = -d1
        return d0 if d0 >= d1 else d1

    target = None
    if resources:
        best = None
        bestd = None
        for r in resources:
            d = dist((sx, sy), r)
            if best is None or d < bestd or (d == bestd and (r[0], r[1]) < (best[0], best[1])):
                best = r
                bestd = d
        target = best

    best_move = (0, 0)
    if target is not None:
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = dist((nx, ny), target)
            score = (d, abs(dx) + abs(dy), dx, dy)
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    cx, cy = (w - 1) // 2, (h - 1) // 2
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = dist((nx, ny), (cx, cy))
        score = (d, abs(dx) + abs(dy), dx, dy)
        if best_move == (0, 0) or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]