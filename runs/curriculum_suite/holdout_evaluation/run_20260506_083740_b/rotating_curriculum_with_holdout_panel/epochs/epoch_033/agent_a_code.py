def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Pick a resource that favors getting there while being far from the opponent
    best_r = None
    best_score = None
    if resources:
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry):
                continue
            myd = md(sx, sy, rx, ry)
            oppd = md(ox, oy, rx, ry)
            val = (oppd - myd) * 10 - myd  # prioritize "stealable" resources; break ties by closeness
            if best_score is None or val > best_score or (val == best_score and myd < best_r[0]):
                best_score = val
                best_r = (myd, rx, ry)

    if best_r is not None:
        tx, ty = best_r[1], best_r[2]
    else:
        tx, ty = w // 2, h // 2

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not valid(nx, ny):
            continue
        myd = md(nx, ny, tx, ty)
        oppd = md(ox, oy, tx, ty)
        # also prefer moves that reduce my distance and, secondarily, increase opponent distance
        val = -myd * 10 + oppd
        # tiny deterministic tie-breaker: favor staying if equal, else prefer lexicographically smaller (via tuple)
        tb = (0 if (dx, dy) == (0, 0) else 1, dx, dy)
        cur = (val, -oppd, tb)
        if best_val is None or cur > best_val:
            best_val = cur
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]