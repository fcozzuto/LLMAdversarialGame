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
        return [0, 0]

    cx, cy = w // 2, h // 2
    best_r = None
    best_s = -10**18
    for rx, ry in resources:
        myd = king_dist(sx, sy, rx, ry)
        oppd = king_dist(ox, oy, rx, ry)
        diff = oppd - myd
        center_bias = king_dist(cx, cy, rx, ry)
        s = 5.0 * diff - 0.9 * (abs(diff)) - 0.18 * center_bias - 0.55 * myd
        if s > best_s:
            best_s = s
            best_r = (rx, ry)

    rx, ry = best_r
    too_close = king_dist(sx, sy, ox, oy) <= 1

    chosen = valid[0]
    best_move_s = -10**18
    for dx, dy, nx, ny in valid:
        myd_next = king_dist(nx, ny, rx, ry)
        oppd_next = king_dist(nx, ny, ox, oy)
        # Interceptor-style: if we're close to the opponent, actively separate; otherwise, collapse on contested target.
        if too_close:
            s = 2.2 * oppd_next - 0.5 * myd_next
        else:
            s = -1.6 * myd_next + 0.25 * oppd_next - 0.1 * king_dist(nx, ny, cx, cy)
        if s > best_move_s:
            best_move_s = s
            chosen = (dx, dy, nx, ny)

    return [chosen[0], chosen[1]]