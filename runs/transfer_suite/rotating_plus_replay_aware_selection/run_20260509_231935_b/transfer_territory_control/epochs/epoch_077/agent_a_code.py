def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obstacles.add((x, y))

    candidates = []
    res = observation.get("resources") or []
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obstacles:
                candidates.append((x, y))
    if not candidates:
        un = observation.get("unclaimed_cells") or []
        for p in un:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                x, y = int(p[0]), int(p[1])
                if inside(x, y) and (x, y) not in obstacles:
                    candidates.append((x, y))
    if not candidates:
        candidates = [(ox, oy), (sx, sy)]

    def mdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    target = None
    bestd = None
    for tx, ty in candidates:
        d = mdist(sx, sy, tx, ty)
        if bestd is None or d < bestd:
            bestd = d
            target = (tx, ty)

    tx, ty = target

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            score = -10**9
        else:
            score = -mdist(nx, ny, tx, ty)
            if (nx, ny) == (ox, oy):
                score -= 3
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]