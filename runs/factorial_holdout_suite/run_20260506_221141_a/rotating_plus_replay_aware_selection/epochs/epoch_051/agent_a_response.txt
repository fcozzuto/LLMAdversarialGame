def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_towards(tx, ty):
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -(cheb(nx, ny, tx, ty))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    if not resources:
        cx = (gw - 1) // 2
        cy = (gh - 1) // 2
        tx = cx - 1 if sx < cx else cx + 1
        ty = cy - 1 if sy < cy else cy + 1
        tx = 3 if gw > 6 else max(0, min(gw - 1, tx))
        ty = 3 if gh > 6 else max(0, min(gh - 1, ty))
        return step_towards(tx, ty)

    best_r = None
    best_score = -10**18
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # prioritize resources we can get earlier; tie-break closer
        score = (d_opp - d_me) * 100 - d_me
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    tx, ty = best_r
    return step_towards(tx, ty)