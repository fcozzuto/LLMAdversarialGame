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

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    res = resources[0]
    if (ox, oy) == (sx, sy):
        pass
    best_need = None
    for rx, ry in resources:
        dself = dist(sx, sy, rx, ry)
        dob = dist(ox, oy, rx, ry)
        need = (dself - dob, dself, rx, ry)
        if best_need is None or need < best_need:
            best_need = need
            res = (rx, ry)
    rx, ry = res

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dself = dist(nx, ny, rx, ry)
        dob = dist(ox, oy, rx, ry)
        # Prefer: closer to target than opponent, then closer, then determinism tie-breaker
        score = (dself - dob, dself, dx, dy)
        if best is None or score < best:
            best = score
            best_move = [dx, dy]

    if best is None:
        return [0, 0]
    return best_move