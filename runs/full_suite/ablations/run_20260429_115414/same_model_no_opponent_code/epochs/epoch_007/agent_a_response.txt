def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = [(int(x), int(y)) for x, y in resources]
    if not res:
        tx, ty = w // 2, h // 2
    else:
        best = None
        for rx, ry in res:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can get first; otherwise closest overall.
            score = (0 if ds < do else 1, (ds - do), ds, rx + ry)
            if best is None or score < best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]

    # Greedy step toward target with slight "contest" pressure (don't allow opponent to close faster).
    cand = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_m = (0, 0)
    best_s = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, nx, ny)  # distance between agents (indirect safety)
        # Predict opponent can move 1 step: reduce contest score if we fall behind.
        opp_min_dist_to_t = cheb(ox, oy, tx, ty) - 1
        # Overall score: minimize distance to target, keep distance from opponent, and maintain lead.
        lead = cheb(nx, ny, tx, ty) - opp_min_dist_to_t
        s = (d_to_t, lead, -d_opp, abs(nx - tx) + abs(ny - ty))
        if best_s is None or s < best_s:
            best_s = s
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]