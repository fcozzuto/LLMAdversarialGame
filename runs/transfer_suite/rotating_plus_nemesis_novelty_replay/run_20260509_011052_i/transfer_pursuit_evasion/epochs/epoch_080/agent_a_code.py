def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    role = (observation.get("self_role") or "").lower()
    is_pursuer = ("pursuer" in role) and ("evader" not in role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    cx = (w - 1) // 2
    cy = (h - 1) // 2

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_d = None
    best_t = None
    best_mv = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, ox, oy)
        t = abs(nx - cx) + abs(ny - cy)
        if best_d is None:
            best_d, best_t, best_mv = d, t, [dx, dy]
            continue
        if is_pursuer:
            if d < best_d or (d == best_d and t < best_t):
                best_d, best_t, best_mv = d, t, [dx, dy]
        else:
            if d > best_d or (d == best_d and t < best_t):
                best_d, best_t, best_mv = d, t, [dx, dy]

    return best_mv