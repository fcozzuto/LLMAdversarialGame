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

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 2 if sx < gw // 2 else 1
        ty = gh - 2 if sy < gh // 2 else 1
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Prefer moves that create the largest lead to some resource over the opponent.
        v = -10**18
        for rx, ry in resources:
            d_self = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            # Immediate pickup favored by higher reward; also discourage moves that help opponent.
            gain = (d_opp - d_self)
            near = 6 - cheb(nx, ny, rx, ry)
            v = v if v > (gain * 3 + near) else (gain * 3 + near)
        # Small tie-break: reduce own distance to the closest resource.
        if v > bestv:
            bestv = v
            best = [dx, dy]
        elif v == bestv:
            if md(nx, ny, resources[0][0], resources[0][1]) < md(sx + best[0], sy + best[1], resources[0][0], resources[0][1]):
                best = [dx, dy]
    return best