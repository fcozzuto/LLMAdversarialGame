def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
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

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    # Choose a target deterministically: nearest resource, tie-break by x,y.
    if resources:
        target = None
        bestd = None
        for x, y in resources:
            d = cheb(sx, sy, x, y)
            if bestd is None or d < bestd or (d == bestd and (x, y) < target):
                bestd = d
                target = (x, y)
    else:
        target = (w // 2, h // 2)

    best_move = (0, 0)
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd = cheb(nx, ny, target[0], target[1])
        od = cheb(ox, oy, target[0], target[1])
        # Prefer moves that reduce our distance; also avoid letting opponent get strictly closer.
        score = myd * 10
        if od < myd:
            score += 40 + (myd - od)
        # Slightly prefer advancing toward the target direction.
        # (Deterministic tie-break by ordering below.)
        adv = (1 if nx - sx != 0 else 0) + (1 if ny - sy != 0 else 0)
        score -= adv
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]