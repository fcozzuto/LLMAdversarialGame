def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(map(tuple, observation.get("obstacles", [])))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx*dx + dy*dy

    # If no resources, drift toward opponent to contest space.
    if not resources:
        tx, ty = ox, oy
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy  # engine will keep us; mirror deterministically

        # Evaluate by best resource swing after this move.
        score_best = None
        for rx, ry in resources:
            self_d = d2(nx, ny, rx, ry)
            opp_d = d2(ox, oy, rx, ry)
            swing = opp_d - self_d  # positive means we get closer relative to opponent
            # Secondary terms: favor nearer self and slightly discourage letting opponent be too close.
            val = (swing, -self_d, -opp_d, rx, ry)
            if score_best is None or val > score_best:
                score_best = val
        # Also add slight global bias: move generally toward the most favorable resource (coarse).
        # Bias toward increasing swing on the currently best resource.
        overall = score_best
        if best is None or overall > best:
            best = overall
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]