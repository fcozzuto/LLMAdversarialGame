def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res_set = set(tuple(p) for p in res)
    rem_cnt = observation.get("remaining_resource_count", len(res))

    best_val = -10**18
    best_move = (0, 0)

    # opponent baseline: how "close" opponent is to the best remaining resource
    # (from opponent's current position)
    opp_best = 10**9
    for r in res:
        d = cheb(ox, oy, r[0], r[1])
        if d < opp_best:
            opp_best = d

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue

            self_best = 10**9
            for r in res:
                d = cheb(nx, ny, r[0], r[1])
                if d < self_best:
                    self_best = d

            val = (opp_best - self_best) * 1000
            if (nx, ny) in res_set:
                val += 10**6  # immediate collection priority
                val += rem_cnt  # collect earlier when more resources remain
            else:
                # slight preference for moving toward resources faster
                val += (2 - self_best) * 10
                # encourage diagonal steps (helps shadow-like opponents traverse corners)
                if dx != 0 and dy != 0:
                    val += 3

            # deterministic tie-break: smallest dx, then dy
            if val > best_val or (val == best_val and (dx < best_move[0] or (dx == best_move[0] and dy < best_move[1]))):
                best_val = val
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]