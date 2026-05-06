def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def d(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best_r = resources[0]
    best_score = None
    for r in resources:
        rx, ry = r
        sd = d(sx, sy, rx, ry)
        od = d(ox, oy, rx, ry)
        score = od - sd  # positive means we are closer than opponent
        key = (score, -sd, -rx, -ry)
        if best_score is None or key > best_score:
            best_score = key
            best_r = r

    tx, ty = best_r
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        sd = d(nx, ny, tx, ty)
        od = d(ox, oy, tx, ty)
        score = od - sd
        key = (score, -sd, dx, dy)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return best_move if best is not None else [0, 0]