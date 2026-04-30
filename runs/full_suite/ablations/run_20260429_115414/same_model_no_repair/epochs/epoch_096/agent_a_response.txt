def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    if not resources:
        return [0, 0]

    def obstacle_penalty(x, y):
        # Penalize proximity to obstacles to reduce getting trapped around chokepoints.
        pen = 0
        for ax, ay in obstacles:
            d = cheb(x, y, ax, ay)
            if d == 0:
                pen += 50
            elif d == 1:
                pen += 7
            elif d == 2:
                pen += 2
        return pen

    # Pick target: strongly prefer resources where opponent is closer, but avoid being lured into obstacle-heavy areas.
    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in blocked:
            continue
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - myd, -(myd + obstacle_penalty(rx, ry) * 0.03), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t
    # Predict opponent greedy one-step move toward the same target.
    def opp_next_dist():
        cur = (ox, oy)
        best_move = (0, 0)
        best = None
        for dx, dy in deltas:
            nx, ny = cur[0] + dx, cur[1] + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            d = cheb(nx, ny, tx, ty)
            # Deterministic tie-break: smaller d, then fixed order by appearance in deltas.
            if best is None or d < best:
                best = d
                best_move = (dx, dy)
        nx, ny = cur[0] + best_move[0], cur[1] + best_move[1]
        return cheb(nx, ny, tx, ty)

    opp_after = opp_next_dist()

    # Choose our move: maximize advantage against target using one-step lookahead for us.
    # Also prevent "stalling" into obstacles by skipping illegal moves.
    cur_best = None
    cur_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        my_after = cheb(nx, ny, tx, ty)
        # Favor moves that reduce distance and also worsen opponent's remaining distance (approx via current greedy prediction).
        # Include obstacle penalty on our next cell to avoid paths that lead to immediate trapping.
        val = (opp_after - my_after, -(my_after + obstacle_penalty(nx, ny) * 0.25), -abs(nx - ox), -abs(ny - oy))
        if cur_best is None or val > cur_best:
            cur_best = val
            cur_move = (dx, dy)

    return [int(cur_move[0]), int(cur_move[1])]