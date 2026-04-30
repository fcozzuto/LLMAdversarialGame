def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # If no resources, move deterministically toward opponent
    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        # try to avoid obstacles on the greedy direction, then cardinal/diagonal components
        for mx, my in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            nx, ny = sx + mx, sy + my
            if (mx == 0 and my == 0) or (inb(nx, ny) and (nx, ny) not in obstacles):
                return [mx, my]
        return [0, 0]

    # Evaluate each legal move by comparing how much earlier we can reach resources than the opponent.
    best_val = -10**18
    best_move = (0, 0)

    # Small preference to keep distance from opponent if tie
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        min_self = 10**9
        min_opp = 10**9
        for rx, ry in resources:
            d_me = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            if d_me < min_self:
                min_self = d_me
            if d_opp < min_opp:
                min_opp = d_opp

        # If we can secure a closer resource than opponent, gain; otherwise reduce.
        val = (min_opp - min_self) * 1000

        # If we are exactly on a resource, strongly prioritize
        if (nx, ny) in set(tuple(p) for p in resources):
            val += 100000

        # Penalize moving closer to opponent when we aren't clearly winning the race
        dist_before = man(sx, sy, ox, oy)
        dist_after = man(nx, ny, ox, oy)
        if val < 0 or dist_after < dist_before:
            val -= (dist_before - dist_after)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]