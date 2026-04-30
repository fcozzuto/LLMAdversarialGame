def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obset = set((x, y) for x, y in obstacles)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    opts = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obset

    if resources:
        best = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd
            score = (margin, -sd)  # prioritize steal margin, then closer
            if best is None or score > best[0]:
                best = (score, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w // 2, h // 2)

    best_move = (0, 0)
    best_score = None
    for dx, dy in opts:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        opp_close = -cheb(nx, ny, ox, oy)  # deterministic mild avoidance/engagement
        on_resource = 1 if (nx, ny) == (tx, ty) else 0
        score = (on_resource, -d, opp_close, -abs(nx - ox) - abs(ny - oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]