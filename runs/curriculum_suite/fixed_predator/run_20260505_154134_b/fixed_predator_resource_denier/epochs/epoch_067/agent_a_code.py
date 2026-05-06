def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -cheb(nx, ny, tx, ty)
            if best is None or v > best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # pick up to 3 most relevant resources (deterministic, no randomness)
    res_sorted = sorted(resources, key=lambda r: (- (cheb(r[0], r[1], ox, oy) - cheb(r[0], r[1], sx, sy)),
                                                cheb(r[0], r[1], sx, sy), r[0], r[1]))
    res_targets = res_sorted[:3]

    best_score = None
    best_move = [0, 0]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        # evaluate move against each target; prefer maximizing win-margin (opp-self distance advantage)
        move_best = None
        for tx, ty in res_targets:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # if we are closer than opp, reward; also reward reducing our distance
            s = (od - sd) * 10 - sd
            if move_best is None or s > move_best:
                move_best = s
        # additional tie-break: try to not give opponent immediate winning reach
        # (minimize opponent distance advantage over our current position for the best target)
        if move_best is None:
            continue
        best_val = move_best
        if best_score is None or best_val > best_score:
            best_score = best_val
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]