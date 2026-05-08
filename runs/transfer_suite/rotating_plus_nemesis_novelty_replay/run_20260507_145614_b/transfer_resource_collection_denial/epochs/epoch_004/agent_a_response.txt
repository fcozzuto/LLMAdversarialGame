def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            cand = (d, dx, dy)
            if cand < best:
                best = cand
        return [best[1], best[2]] if best[0] != 10**9 else [0, 0]

    best_move = (10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        local_best = (10**18, 10**18)
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = myd - opd  # smaller => we arrive sooner
            # tie-break: closer is better; also prefer resources that are further from us next-turn if tied
            cand = (adv, myd)
            if cand < local_best:
                local_best = cand
        # additional preference for moves that directly reduce distance to the currently best resource
        overall = (local_best[0], local_best[1], cheb(nx, ny, (ox + sx) // 2, (oy + sy) // 2))
        if overall < best_move:
            best_move = (overall[0], dx, dy)

    return [best_move[1], best_move[2]] if best_move[0] != 10**18 else [0, 0]