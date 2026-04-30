def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_tuple = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue

        our_near = 10**9
        opp_near = 10**9
        best_adv = -10**9
        worst_adv = 10**9

        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            if our_d < our_near:
                our_near = our_d
            if opp_d < opp_near:
                opp_near = opp_d
            adv = opp_d - our_d  # positive: we are closer than opponent
            if adv > best_adv:
                best_adv = adv
            if adv < worst_adv:
                worst_adv = adv

        # Prefer: create max advantage; then improve our nearest; then reduce opponent nearest.
        cand_tuple = (best_adv, -our_near, -opp_near, worst_adv, -abs(dx) - abs(dy), dx, dy)
        if best_tuple is None or cand_tuple > best_tuple:
            best_tuple = cand_tuple
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]