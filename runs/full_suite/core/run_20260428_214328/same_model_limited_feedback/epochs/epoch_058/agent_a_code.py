def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_dist_cache = {}
    best = None
    best_val = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources opponent is much farther from; break ties by our proximity.
        val = (do - ds, -ds, rx, ry)
        if best is None or val > best_val:
            best = (rx, ry)
            best_val = val
    tx, ty = best

    deltas = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    best_move = [0, 0]
    best_mval = None

    for dx, dy in deltas:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Greedy toward target, but keep away from opponent if close.
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(nx, ny, ox, oy)
        # Tie-break: maximize distance from opponent; then prefer diagonal/forward slightly by dx/dy sum.
        mval = (-ds2, do2, abs(dx)+abs(dy), dx, dy)
        if best_mval is None or mval > best_mval:
            best_mval = mval
            best_move = [dx, dy]

    return best_move