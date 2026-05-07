def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def steps(x, y, rx, ry):
        return max(abs(rx - x), abs(ry - y))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    # If already on a resource, prefer staying still.
    rset = set(tuple(r) for r in resources)
    if (sx, sy) in rset and valid(sx, sy):
        return [0, 0]

    best = (-(10**12), -(10**12), 10**9, 0, 0)
    # score tuple: (best_lead, -opp_proximity_sum, self_dist_to_target, closer_to_any, dx_then_dy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        best_lead = -(10**12)
        best_self = 10**9
        best_closest_any = 10**9
        opp_sum = 0
        for rx, ry in resources:
            sdist = steps(nx, ny, rx, ry)
            odist = steps(ox, oy, rx, ry)
            lead = odist - sdist
            if lead > best_lead or (lead == best_lead and (sdist < best_self)):
                best_lead = lead
                best_self = sdist
            if sdist < best_closest_any:
                best_closest_any = sdist
            opp_sum += odist
        opp_prox = -opp_sum
        cand = (best_lead, opp_prox, best_self, -best_closest_any, dx, dy)
        if cand > best:
            best = cand

    dx, dy = best[-2], best[-1]
    nx, ny = sx + dx, sy + dy
    if valid(nx, ny):
        return [dx, dy]
    return [0, 0]