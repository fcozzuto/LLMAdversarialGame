def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Opponent baseline: its nearest resource (tie by position)
    opp_nearest = None
    opp_best = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        key = (d, rx, ry)
        if opp_best is None or key < opp_best:
            opp_best = key
            opp_nearest = (rx, ry)

    # For us: target resource is our nearest, but we also prefer targets that
    # reduce/deny opponent approach to their current nearest.
    parity = observation.get("turn_index", 0) & 1
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        our_nearest = None
        our_best = None
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            key = (d, rx, ry)
            if our_best is None or key < our_best:
                our_best = key
                our_nearest = (rx, ry)

        tx, ty = our_nearest
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)

        # "Disruption": how much this target worsens opponent's access to its current nearest
        rx0, ry0 = opp_nearest
        d_opp0_before = cheb(ox, oy, rx0, ry0)
        # approximate effect: if we head toward a resource close to opponent's nearest,
        # we are more likely to contest the region (deterministic proxy)
        contest = -cheb(tx, ty, rx0, ry0)

        # Also slightly prefer cutting off by increasing opponent's distance to our target
        opp_worsen = d_opp

        val = (-(d_self) * 1000) + (opp_worsen * 10) + contest
        if parity == 0:
            val += -((tx + ty) & 7)
        else:
            val += -((abs(ox - tx) + abs(oy - ty)) & 7)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]