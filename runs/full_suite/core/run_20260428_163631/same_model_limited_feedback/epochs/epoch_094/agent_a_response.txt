def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]

    obs = set((p[0], p[1]) for p in obstacles)
    res_set = set((p[0], p[1]) for p in resources)

    if (sx, sy) in res_set:
        return [0, 0]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    # Pick best target resource: minimize (self_dist - opp_dist)
    cur = (sx, sy)
    opp = (ox, oy)
    best = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        sd = dist(cur, (rx, ry))
        od = dist(opp, (rx, ry))
        key = (sd - od, sd, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    if best is None:
        # No visible resources; drift to center
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best[1]

    # Choose move that best approaches target while avoiding obstacles
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        nd = dist((nx, ny), (tx, ty))
        cd = dist(cur, (tx, ty))
        improves = 1 if nd < cd else 0
        # Also prefer not moving away from where opponent could be blocking
        nd_opp = dist((nx, ny), opp)
        key = (nd, -improves, -nd_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]