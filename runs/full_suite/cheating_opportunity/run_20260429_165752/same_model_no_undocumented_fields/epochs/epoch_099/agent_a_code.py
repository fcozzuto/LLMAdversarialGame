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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    if not ok(sx, sy):
        for dx, dy in moves:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    best = None
    best_score = None

    if resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            mind = 10**9
            for rx, ry in resources:
                d = abs(nx - rx)
                e = abs(ny - ry)
                d = d if d > e else e
                if d < mind:
                    mind = d
            score = mind
            if best_score is None or score < best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
    else:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = abs(nx - ox) + abs(ny - oy)
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]