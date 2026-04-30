def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    if resources:
        best_dir = (0, 0)
        bestv = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            mind = 10**18
            for rx, ry in resources:
                v = d2(nx, ny, rx, ry)
                if v < mind:
                    mind = v
            ov = d2(nx, ny, ox, oy)
            score = mind * 10 + ov  # prefer closer to resources; mildly avoid getting too close to opponent
            if score < bestv:
                bestv = score
                best_dir = (dx, dy)
        return [int(best_dir[0]), int(best_dir[1])]

    # No visible resources: move toward the midpoint of (opponent) and nearest edge toward self side
    tx = (ox + (w - 1 if ox < sx else 0)) // 2
    ty = (oy + (h - 1 if oy < sy else 0)) // 2
    best_dir = (0, 0)
    bestv = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = d2(nx, ny, tx, ty)
        if score < bestv:
            bestv = score
            best_dir = (dx, dy)
    return [int(best_dir[0]), int(best_dir[1])]