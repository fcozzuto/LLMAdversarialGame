def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    res = [tuple(r) for r in resources]
    res_set = set(res)

    # If we can take a resource immediately, do it.
    if (sx, sy) in res_set:
        return [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) in res_set and (nx, ny) not in obstacles:
            return [dx, dy]

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Our best race target from (nx,ny)
        self_best = 10**9
        opp_best = 10**9
        for rx, ry in res:
            d_s = dist(nx, ny, rx, ry)
            if d_s < self_best:
                self_best = d_s
            d_o = dist(ox, oy, rx, ry)
            if d_o < opp_best:
                opp_best = d_o

        # Move value: maximize our advantage vs opponent's closest threat
        # Also slightly prefer moves that reduce our distance to any resource.
        val = (opp_best - self_best) * 1000 - self_best

        # Deterministic tie-break: prefer staying still last (avoid oscillation)
        if val > best_val or (val == best_val and (dx, dy) == (0, 0) and best_move != [0, 0]):
            best_val = val
            best_move = [dx, dy]

    return best_move