def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if not res:
            cand = (0, -cheb(nx, ny, ox, oy), -nx, -ny)
        else:
            # For this move, estimate our best resource arrival time vs opponent's best.
            # Choose move that maximizes (opp_time_to_our_target - our_time_to_target),
            # i.e., tries to arrive before the opponent to some resource.
            best_local = None
            for rx, ry in res:
                self_t = cheb(nx, ny, rx, ry)
                opp_t = cheb(ox, oy, rx, ry)
                gap = opp_t - self_t
                # Prefer smaller self_t if gaps tie; then prefer nearer to opponent (interception pressure).
                key = (gap, -self_t, -abs(nx - ox) - abs(ny - oy), -rx, -ry)
                if best_local is None or key > best_local:
                    best_local = key
            cand = best_local
        if best is None or cand > best:
            best = cand
            best_move = [dx, dy]

    if best is None:
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]
    return best_move