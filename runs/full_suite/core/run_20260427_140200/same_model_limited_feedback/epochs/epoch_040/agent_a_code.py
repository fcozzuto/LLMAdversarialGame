def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    res_set = set((x, y) for x, y in resources)
    obs_set = set((x, y) for x, y in obstacles)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    # Opponent baseline: how close is opponent to any resource?
    opp_best_d = 10**9
    for r in res_set:
        d = dist((ox, oy), r)
        if d < opp_best_d:
            opp_best_d = d
    if not res_set:
        opp_best_d = 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue

        if res_set:
            my_best_d = 10**9
            for r in res_set:
                d = dist((nx, ny), r)
                if d < my_best_d:
                    my_best_d = d
        else:
            my_best_d = 0

        score = 0
        if (nx, ny) in res_set:
            score += 50  # immediate resource
        score += -my_best_d

        # Try to "beat" opponent to the closest resource.
        if my_best_d < opp_best_d:
            score += 8
        elif my_best_d == opp_best_d:
            score += 2

        # Slight preference for reducing distance to opponent to contest space/resources.
        score += -0.1 * dist((nx, ny), (ox, oy))

        # Deterministic tie-break: fixed move order plus coordinate preference.
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]