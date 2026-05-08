def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = [0, 0]
    bestv = -10**18

    # Precompute baseline opponent proximity to resources
    res_list = [(r[0], r[1]) for r in resources if isinstance(r, (list, tuple)) and len(r) == 2]
    if not res_list:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = -(abs(nx - tx) + abs(ny - ty)) + 0.05 * (abs(nx - ox) + abs(ny - oy))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        wins = 0
        tie_best = 10**9
        opp_adv_min = 10**9
        self_adv_sum = 0

        for rx, ry in res_list:
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            d = od - sd  # positive is good
            self_adv_sum += d
            if sd < od:
                wins += 1
                if (od - sd) < tie_best:
                    tie_best = od - sd
            else:
                if (sd - od) < opp_adv_min:
                    opp_adv_min = sd - od

        # If we can secure any resource first, prioritize that; otherwise maximize (od-sd) overall.
        # Add a small term to also reduce our distance to opponent's nearest resource.
        opp_nearest = min((abs(ox - rx) + abs(oy - ry), rx, ry) for rx, ry in res_list)[0]
        v = 0
        if wins > 0:
            # Prefer more "wins", and then closer-to-completing earliest secured resources (tie_best smaller is better)
            v = 200 * wins - 3 * tie_best
        else:
            v = 2.0 * self_adv_sum - 0.02 * opp_nearest

        # Obstacle-aware nudge: discourage moving away from any resource
        nearest_res = min(man((nx, ny), (rx, ry)) for rx, ry in res_list)
        v -= 0.05 * nearest_res

        if v > bestv:
            bestv = v
            best = [dx, dy]

    return best