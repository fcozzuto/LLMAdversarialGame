def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # 8-neighborhood + stay
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    res_set = set(tuple(r) for r in resources)

    late = 1 if turns_remaining <= 10 else 0
    best_val = -10**18
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy

        # Immediate pickup
        val = 0
        if (nx, ny) in res_set:
            val += 10**7

        # Evaluate resources: prefer ones where we are ahead of opponent; else deny-deny by moving toward
        # resources where opponent is close (so we can steal/contest).
        my_best = 10**9
        opp_best = 10**9
        gap_best = -10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd < my_best: my_best = myd
            if opd < opp_best: opp_best = opd
            gap = opd - myd  # positive means we are closer than opponent
            if gap > gap_best: gap_best = gap

        # Late game: greedily minimize our distance; early: maximize advantage gap and also avoid being too far.
        if late:
            val += 10**5 * (-my_best)
        else:
            val += 10**6 * gap_best
            val += 10**3 * (-my_best)

            # If we're behind everyone, try to "cut off" by moving toward closest opponent-leaning resource.
            if gap_best < 0:
                val += 10**4 * (-opp_best + my_best)

        # Slight preference for staying mobile toward center-ish to reduce loops deterministically
        # without global search.
        val += -1 * (abs(nx - 3.5) + abs(ny - 3.5))

        if val > best_val:
            best_val = val
            best_move = [nx - sx, ny - sy]

    return best_move