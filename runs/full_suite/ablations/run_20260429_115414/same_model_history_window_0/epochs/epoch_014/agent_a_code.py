def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    res_list = [(p[0], p[1]) for p in resources if (p[0], p[1]) not in obs_set]

    def cheb(a, b, c, d):  # distance with diagonal moves
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy  # squared
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not res_list:
        # no resources: head toward center while avoiding obstacles
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obs_set:
                continue
            d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    best_target = None
    for rx, ry in res_list:
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        advantage = d_opp - d_self
        closer = 1 if d_self < d_opp else 0
        # Prefer being closer; otherwise pick where opponent is farthest relative to us.
        key = (-closer, -advantage, d_self, rx, ry)
        if best_target is None or key < best_target[0]:
            best_target = (key, (rx, ry))
    tx, ty = best_target[1]

    # Choose move that reduces distance to target; break ties by moving away from opponent and lexicographic order.
    best_move = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs_set:
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # also slightly prefer moves that avoid getting stuck near obstacles (local count)
        neigh_obs = 0
        for mx, my in moves:
            px, py = nx + mx, ny + my
            if inside(px, py) and (px, py) in obs_set:
                neigh_obs += 1
        cand = (d_to_t, -d_opp, neigh_obs, dx, dy)
        if best_move is None or cand < best_move[0]:
            best_move = (cand, (dx, dy))
    if best_move is None:
        return [0, 0]
    return [best_move[1][0], best_move[1][1]]