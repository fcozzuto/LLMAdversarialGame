def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, (0, 0))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h: 
                continue
            if (nx, ny) in obstacles:
                continue
            v = cheb(nx, ny, tx, ty)
            key = (v, dx, dy)
            if key < (best[0], best[1][0], best[1][1]):
                best = (v, (dx, dy))
        return [best[1][0], best[1][1]]

    # Choose move maximizing relative closeness to a resource (we want ds - do to be small).
    best_move = (10**18, (0, 0))
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        cur_best = 10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we can reach sooner than opponent, strongly prefer it.
            rel = ds - do
            # Encourage picking up by also slightly preferring absolute closeness.
            val = rel * 1000 + ds
            if val < cur_best:
                cur_best = val

        # If multiple moves give same cur_best, use smaller distance to opponent (disruption) as secondary.
        opp_dist = cheb(nx, ny, ox, oy)
        key = (cur_best, opp_dist, dx, dy)
        if key < (best_move[0], best_move[1][0], best_move[1][1], best_move[1][1]):
            best_move = (cur_best, (dx, dy))

    return [best_move[1][0], best_move[1][1]]