def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not res:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_sc = -10**18
    # Deterministic tie-breaker order by deltas sequence
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Choose the resource that maximizes "race advantage" after our move
        move_best = -10**18
        for rx, ry in res:
            sd = manh(nx, ny, rx, ry)
            od_est = manh(ox, oy, rx, ry) - 1  # opponent gets one step after us
            if od_est < 0:
                od_est = 0
            # Strong preference for winning the race, small preference for shorter own distance
            sc = (od_est - sd) * 1000 - sd
            if sc > move_best:
                move_best = sc

        if move_best > best_sc:
            best_sc = move_best
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]