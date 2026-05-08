def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if (sx, sy) in map(tuple, resources):
        return [0, 0]

    # 1-step lookahead: choose move maximizing advantage over best resource target
    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        # If we land on a resource, strongly prefer it
        val = 0
        if (nx, ny) in map(tuple, resources):
            val += 10**6

        # Evaluate by picking our best reachable resource vs opponent best
        my_best = -10**9
        opp_best = 10**9
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer resources where we're closer after this move
            my_best = max(my_best, (d_opp - d_self))
            opp_best = min(opp_best, d_opp)

        # Tie-break toward earlier collection: smaller self distance to closest resource
        my_closest = 10**9
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            if d_self < my_closest:
                my_closest = d_self

        # Heuristic: maximize advantage, then minimize our distance, then maximize closeness gap
        val += my_best * 1000
        val += (40 - my_closest)
        val -= opp_best * 2

        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]
    return best