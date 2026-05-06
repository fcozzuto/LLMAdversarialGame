def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    resources.sort()
    best = [0, 0]
    best_score = None

    if resources:
        tx, ty = min(resources, key=lambda p: (dist(sx, sy, p[0], p[1]), p[0], p[1]))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            cur = dist(nx, ny, tx, ty)
            opp = dist(nx, ny, ox, oy)
            score = (-cur, -opp, dx, dy)
            if best_score is None or score > best_score:
                best_score = score
                best = [dx, dy]
        return [int(best[0]), int(best[1])]

    cx, cy = w // 2, h // 2
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        score = (-dist(nx, ny, cx, cy), dist(nx, ny, ox, oy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return [int(best[0]), int(best[1])]