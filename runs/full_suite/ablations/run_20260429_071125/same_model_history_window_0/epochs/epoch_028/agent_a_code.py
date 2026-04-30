def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    my = observation["self_position"]; op = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    ox, oy = op; mx, myy = my

    def best_res_dist(pos):
        if not resources:
            return 999
        x, y = pos
        bd = 999
        for rx, ry in resources:
            d = abs(rx - x) + abs(ry - y)
            if d < bd: bd = d
        return bd

    my_d = best_res_dist((mx, myy))
    op_d = best_res_dist((ox, oy))
    behind = op_d < my_d

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None; bestv = -10**18

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    for dx, dy in deltas:
        nx, ny = mx + dx, myy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        nd_my = best_res_dist((nx, ny))
        nd_op = best_res_dist((ox, oy))  # assume opponent position unchanged this turn
        # Encourage pushing opponent away when behind; otherwise focus on our resource access.
        v = (nd_op - nd_my)
        if behind:
            # Move toward opponent to increase chance of interference.
            v += 0.5 * (abs(ox - mx) + abs(oy - myy) - (abs(ox - nx) + abs(oy - ny)))
        # Small deterministic preference for staying if tied later: handled by delta order.
        if v > bestv:
            bestv = v; best = [dx, dy]

    if best is None:
        return [0, 0]
    return best