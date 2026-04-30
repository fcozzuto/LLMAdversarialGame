def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            own = 10**6
            opp = 10**6
            for rx, ry in resources:
                d1 = cheb(nx, ny, rx, ry)
                d2 = cheb(ox, oy, rx, ry)
                if d1 < own: own = d1
                if d2 < opp: opp = d2
            # If we can win the closest resource race, go for it; otherwise, steer away.
            score = -own + 0.5 * (opp - own)
            if (sx, sy) == (nx, ny):
                score -= 0.1
            if dx == 0 and dy == 0:
                score -= 0.2
            if score > best_score:
                best_score = score
                best = (dx, dy)
    else:
        # No visible resources: move to maximize distance from opponent.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = cheb(nx, ny, ox, oy)
            if (dx, dy) == (0, 0):
                score -= 0.2
            if score > best_score:
                best_score = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]