def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def steps(x, y, rx, ry):
        return max(abs(rx - x), abs(ry - y))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    res = [tuple(r) for r in resources]
    best_move = (0, 0)
    best_val = -10**18
    # deterministic move ordering preference: center-first, then smaller dx, then smaller dy
    ordered = sorted(dirs, key=lambda d: (abs(d[0])+abs(d[1]), d[0], d[1]))

    for dx, dy in ordered:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate best "winning" resource from this next position.
        best_lead = -10**18
        best_self_t = 10**18
        best_opp_t = 10**18
        best_resource = None

        for rx, ry in res:
            st = steps(nx, ny, rx, ry)
            ot = steps(ox, oy, rx, ry)
            lead = ot - st  # positive means we arrive earlier
            if lead > best_lead or (lead == best_lead and (st < best_self_t or (st == best_self_t and ot < best_opp_t))):
                best_lead = lead
                best_self_t = st
                best_opp_t = ot
                best_resource = (rx, ry)

        # Value shaping: prioritize winning lead, then closeness (lower self time).
        if best_lead > 0:
            win_bonus = 2000
        else:
            win_bonus = 0
        dist_bias = best_self_t
        # slight preference to reduce opponent's advantage even if not winning
        opp_pressure = -min(0, best_lead)

        val = win_bonus + (best_lead * 100) - (dist_bias * 3) + opp_pressure
        # tiny deterministic tie-break: prefer moving toward the best resource
        if best_resource is not None:
            rx, ry = best_resource
            val += - (abs(rx - nx) + abs(ry - ny)) * 0.01

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]