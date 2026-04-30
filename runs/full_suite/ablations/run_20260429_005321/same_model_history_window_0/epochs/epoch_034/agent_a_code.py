def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = [(p[0], p[1]) for p in observation["resources"]]
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        dx = a - c; dy = b - d
        return (dx*dx + dy*dy) ** 0.5

    # Pick target resource where we are relatively closer than opponent
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        md = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        # Prefer resources where (my_dist - 0.9*opp_dist) is small; also break ties by absolute closeness
        key = (md - 0.9 * od, md)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    # If no resources (edge case), move to increase distance from opponent and toward center
    if best is None:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        def eval_move(nx, ny):
            d_op = dist(nx, ny, ox, oy)
            d_ctr = dist(nx, ny, tx, ty)
            return d_op + 0.2 * d_ctr
    else:
        tx, ty = best
        # If opponent is much closer to our nearest target, bias more toward blocking/interception near their path
        opp_better = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            od = dist(ox, oy, rx, ry)
            if opp_better is None or od < opp_better[0]:
                opp_better = (od, rx, ry)
        opp_target = (opp_better[1], opp_better[2]) if opp_better else (tx, ty)

        def eval_move(nx, ny):
            if (nx, ny) in obstacles:
                return -1e9
            myd = dist(nx, ny, tx, ty)
            opd = dist(nx, ny, ox, oy)
            # Secondary objective: if opponent is targeting the same region, slightly prioritize moving toward their target too
            inter = dist(nx, ny, opp_target[0], opp_target[1]) if opp_target else 0.0
            # Tertiary: stay away from opponent while moving toward target
            return (-myd) + 0.15 * opd - 0.06 * inter

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        val = eval_move(nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]