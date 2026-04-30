def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    opp_target = None
    if resources:
        bestd = 10**9
        for r in resources:
            d = dist((ox, oy), (r[0], r[1]))
            if d < bestd:
                bestd = d
                opp_target = (r[0], r[1])

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            val = -10**12
        else:
            val = 0
            if resources:
                ns = (nx, ny)
                # Choose resource where we can gain the most proximity advantage over opponent
                best_adv = -10**9
                best_self_d = 10**9
                for r in resources:
                    rr = (r[0], r[1])
                    ds = dist(ns, rr)
                    do = dist((ox, oy), rr)
                    adv = do - ds
                    if adv > best_adv or (adv == best_adv and ds < best_self_d):
                        best_adv = adv
                        best_self_d = ds
                # Favor high proximity advantage, then closeness
                val += best_adv * 20 - best_self_d
                # Additional pressure: reduce opponent's distance to their nearest resource
                if opp_target is not None:
                    val += -(dist((nx, ny), opp_target)) * 0.5
                    # Slightly increase chance to "interfere" near the opponent's target path by pushing toward it
                    # and away from our own being stuck: balance with opponent distance
                val += -dist((nx, ny), (ox, oy)) * 0.05
            else:
                val = -dist((nx, ny), (ox, oy))
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]