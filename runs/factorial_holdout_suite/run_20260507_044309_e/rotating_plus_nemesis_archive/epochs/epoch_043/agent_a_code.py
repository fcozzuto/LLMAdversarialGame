def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for b in obstacles:
        try:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))
        except:
            pass

    res = []
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                res.append((rx, ry))
        except:
            pass
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def opponent_after_one(target, ax, ay):
        best = 10**9
        for dx, dy in deltas:
            nx, ny = ax + dx, ay + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, target[0], target[1])
            if d < best:
                best = d
        if best == 10**9:
            return cheb(ax, ay, target[0], target[1])
        return best

    best_move = (0, 0)
    best_val = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        our_best = 10**9
        opp_best = 10**9
        for t in res:
            d_our = cheb(nx, ny, t[0], t[1])
            if d_our < our_best:
                our_best = d_our
                # assume opponent also targets this nearest resource (race heuristic)
                opp_best = opponent_after_one(t, ox, oy)
        val = opp_best - our_best
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move == (0, 0) and not valid(sx, sy):
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]