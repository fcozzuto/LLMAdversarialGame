def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def target_value(tx, ty, mx, my):
        d_me = abs(tx - mx) + abs(ty - my)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_me
        return lead * 1000 - d_me + 0.01 * d_opp

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Deterministic preference order via lexicographic on move
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        # pick best reachable target from next position
        local_best = -10**18
        for tx, ty in resources:
            tv = target_value(tx, ty, nx, ny)
            if tv > local_best:
                local_best = tv
        # encourage reducing opponent's distance slightly even if lead ties
        opp_pressure = -man((nx, ny), (ox, oy))
        # add small tie-break favoring closer to any resource
        min_res = min(man((nx, ny), r) for r in resources)
        score = local_best + 0.1 * opp_pressure - 0.01 * min_res
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    # If every move was invalid (unlikely), fall back to directional toward best nominal target
    if (dx, dy) == (0, 0) and (x, y) in obstacles:
        best_t = resources[0]
        best_tv = target_value(best_t[0], best_t[1], x, y)
        for tx, ty in resources[1:]:
            tv = target_value(tx, ty, x, y)
            if tv > best_tv:
                best_tv = tv
                best_t = (tx, ty)
        return [sign(best_t[0] - x), sign(best_t[1] - y)]
    return [int(dx), int(dy)]