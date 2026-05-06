def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)
    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)
    def blocked(nx, ny):
        return (nx, ny) in obstacles
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    def resource_value(tx, ty, px, py):
        d_me = abs(tx - px) + abs(ty - py)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_me
        return lead * 1000 - d_me + d_opp * 0.001

    best_delta = (0, 0)
    best_score = -10**18
    best_mdist = 10**9

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            nx, ny = x, y
        local_best = -10**18
        local_best_m = 10**9
        for r in resources:
            tx, ty = r[0], r[1]
            v = resource_value(tx, ty, nx, ny)
            m = man(tx, ty, nx, ny)
            if v > local_best or (v == local_best and m < local_best_m):
                local_best = v
                local_best_m = m
        if (local_best > best_score) or (local_best == best_score and local_best_m < best_mdist) or \
           (local_best == best_score and local_best_m == best_mdist and (dx, dy) < best_delta):
            best_score = local_best
            best_mdist = local_best_m
            best_delta = (dx, dy)

    return [best_delta[0], best_delta[1]]