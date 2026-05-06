def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]
    if not resources:
        best = min(valid, key=lambda m: king_dist(m[2], m[3], w // 2, h // 2))
        return [best[0], best[1]]

    cx, cy = w // 2, h // 2
    best_score = -10**18
    best_move = (0, 0)

    for dx, dy, nx, ny in valid:
        opp_now = king_dist(nx, ny, ox, oy)
        prox_pen = 1.6 if opp_now <= 1 else (0.7 if opp_now <= 2 else 0.0)
        center_bias = king_dist(cx, cy, nx, ny)
        local_best = -10**18
        for rx, ry in resources:
            myd = king_dist(nx, ny, rx, ry)
            oppd = king_dist(ox, oy, rx, ry)
            diff = oppd - myd
            s = 5.0 * diff - 0.25 * myd - 0.12 * center_bias - 0.55 * abs(diff)
            if diff > 0 and myd == 0:
                s += 50
            local_best = s if s > local_best else local_best
        s2 = local_best - prox_pen
        if s2 > best_score:
            best_score = s2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]