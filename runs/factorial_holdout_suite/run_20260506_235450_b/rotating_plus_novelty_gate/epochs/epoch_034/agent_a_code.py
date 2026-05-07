def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if is_free(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]
    if not resources:
        return [0, 0]

    best_res = None
    best_score = -10**18
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        score = od - sd
        if best_res is None or score > best_score:
            best_res, best_score = (rx, ry), score
    rx, ry = best_res if best_res is not None else (sx, sy)

    best_move = (0, 0, sx, sy)
    best_d = None
    best_secondary = None
    for dx, dy, nx, ny in moves:
        sd = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        secondary = od - sd
        if best_d is None or sd < best_d or (sd == best_d and secondary > best_secondary):
            best_d, best_secondary = sd, secondary
            best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]