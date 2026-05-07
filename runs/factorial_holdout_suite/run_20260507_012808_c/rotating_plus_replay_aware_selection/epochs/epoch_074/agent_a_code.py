def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    res_set = set((r[0], r[1]) for r in resources)
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    def cheb(a, b, c, d):
        return max(abs(c - a), abs(d - b))

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        if (nx, ny) in res_set:
            val = 10**9
        else:
            val = 0

        # Evaluate best resource we could secure vs opponent's likely greedy movement
        local_best = -10**18
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            # opponent greedy: move one step (Chebyshev) toward (rx,ry), then distance
            odx = 0 if rx == ox else (1 if rx > ox else -1)
            ody = 0 if ry == oy else (1 if ry > oy else -1)
            tox, toy = ox + odx, oy + ody
            if not valid(tox, toy):
                tox, toy = ox, oy
                odx = 0
                ody = 0
            opp_d = cheb(tox, toy, rx, ry)

            # Prefer capturing/being closer; penalize being behind
            if self_d == 0:
                score = 2 * 10**6 - opp_d
            else:
                score = (opp_d - self_d) * 1000 - self_d * 2 + (0 if self_d <= opp_d else -5000)
            if score > local_best:
                local_best = score

        # Also slightly prefer moves that reduce distance to the nearest resource (robustness)
        nearest_d = min(cheb(nx, ny, r[0], r[1]) for r in resources)
        val += local_best + (100 - nearest_d)

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [best_move[0], best_move[1]]