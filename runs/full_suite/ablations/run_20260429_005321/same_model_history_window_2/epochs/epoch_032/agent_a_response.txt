def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Predict opponent greedy target: nearest resource to opponent (deterministic tie-break).
    target = (ox, oy)
    bestd = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if bestd is None or d < bestd or (d == bestd and (rx, ry) < target):
            bestd = d
            target = (rx, ry)

    tx, ty = target

    best_mv = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)

        # Core: make ourselves as close as possible to opponent's predicted target.
        # Secondary: prevent opponent from staying strictly closer.
        score = (opd - myd, -myd)

        # If we can also steal any other near resource this turn, bump priority.
        if resources:
            steal = 0
            for rx, ry in resources:
                if cheb(nx, ny, rx, ry) <= 1 and cheb(ox, oy, rx, ry) >= 2:
                    steal += 1
            score = (score[0] + 3 * steal, score[1])

        if best_score is None or score > best_score:
            best_score = score
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]