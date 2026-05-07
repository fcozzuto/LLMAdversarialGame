def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def mhd(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        # try any safe move toward center
        best = [0, 0]
        best_d = 10**9
        for ddx, ddy in dirs:
            nx, ny = sx + ddx, sy + ddy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            d = mhd(nx, ny, tx, ty)
            if d < best_d:
                best_d = d
                best = [ddx, ddy]
        return best

    best_r = resources[0]
    best_key = None
    # denial-aware: prefer resources we can reach sooner; if tie, prefer closer to target and farther from opponent.
    for rx, ry in resources:
        sd = mhd(sx, sy, rx, ry)
        od = mhd(ox, oy, rx, ry)
        adj = 1 if sd <= 1 else 0
        key = (adj, od - sd, -sd, -((rx - w // 2) ** 2 + (ry - h // 2) ** 2))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    cur_dist = mhd(sx, sy, rx, ry)

    best_move = [0, 0]
    best_val = (-10**9, 10**9)
    # choose move that decreases distance to target; break ties by increasing opponent distance
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        if (dx, dy) == (0, 0) and cur_dist == 0:
            return [0, 0]
        nd = mhd(nx, ny, rx, ry)
        if nd > cur_dist + 1:
            continue
        opp_nd = mhd(ox, oy, rx, ry)
        val = (-(nd), -(opp_nd), -((nx - rx) ** 2 + (ny - ry) ** 2))
        # primary: nd smaller, secondary: avoid giving opponent too much tempo by preferring moves with nd <= cur_dist
        primary = -nd
        if primary > best_val[0] or (primary == best_val[0] and nd < best_val[1]):
            best_val = (primary, nd)
            best_move = [dx, dy]

    return best_move