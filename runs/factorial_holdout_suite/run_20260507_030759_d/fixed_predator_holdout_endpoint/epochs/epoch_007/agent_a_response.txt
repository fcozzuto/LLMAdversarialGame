def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_raw) if obstacles_raw else set()

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_step_to(tx, ty):
        best = [0, 0]
        best_d = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            if best_d is None or d < best_d or (d == best_d and (dx, dy) < (best[0], best[1])):
                best_d = d
                best = [dx, dy]
        return best

    if not resources:
        cx, cy = w // 2, h // 2
        return best_step_to(cx, cy)

    best_r = None
    best_s = None
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer reachable resources that we can contest; if opponent is closer, penalize strongly
        penalty = 0 if od >= sd else 4 * (sd - od)
        s = sd + penalty
        if best_s is None or s < best_s or (s == best_s and (sd, -od, rx, ry) < (cheb(sx, sy, best_r[0], best_r[1]), -cheb(ox, oy, best_r[0], best_r[1]), best_r[0], best_r[1])):
            best_s = s
            best_r = [rx, ry]

    if best_r is None:
        cx, cy = w // 2, h // 2
        return best_step_to(cx, cy)

    return best_step_to(best_r[0], best_r[1])