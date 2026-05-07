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

    def manh(a, b, c, d):
        return abs(a - c) + abs(b - d)

    resources = sorted([(r[0], r[1]) for r in res], key=lambda t: (t[0], t[1]))
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Strategy: maximize estimated "race margin" = (opponent can reduce distance next turn) - (our distance after our move)
        local_best = -10**18
        local_closest = 10**9
        for rx, ry in resources:
            sd = manh(nx, ny, rx, ry)
            od = manh(ox, oy, rx, ry)
            est_od_after = od - 1
            if est_od_after < 0:
                est_od_after = 0
            margin = est_od_after - sd
            if margin > local_best:
                local_best = margin
            if sd < local_closest:
                local_closest = sd

        # If we can't beat anyone (margin <= 0), still push toward the closest resource to deny.
        score = local_best * 1000 - local_closest
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move