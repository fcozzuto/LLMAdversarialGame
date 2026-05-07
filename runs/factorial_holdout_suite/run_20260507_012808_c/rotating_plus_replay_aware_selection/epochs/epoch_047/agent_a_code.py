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
        # Chebyshev distance for diagonal moves allowed, uniform cost per step
        return max(abs(rx - x), abs(ry - y))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    best_move = (0, 0)
    best_val = -10**18

    # Prefer moves that let us arrive at some resource strictly earlier, then maximize earliest lead.
    # Also add small bias toward closer-to-any-resource and away from being blocked.
    res_list = [tuple(r) for r in resources]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate top resource we can "win" (arrive earlier) from this next position.
        # If already on a resource, prioritize immediately.
        value = 0
        local_best = -10**18
        for rx, ry in res_list:
            sm = steps(nx, ny, rx, ry)
            so = steps(ox, oy, rx, ry)
            lead = so - sm  # positive means we are earlier
            if lead > 0:
                # Strongly prefer immediate/near-term winning
                cand = 1000000 - sm * 1000 + lead * 500
            else:
                # Don't completely ignore resources; make it a secondary objective
                cand = -sm * 10 - abs(lead) * 5
            if cand > local_best:
                local_best = cand

        # Additional deterministic biases:
        # - If we are on a resource next step, that's the best possible.
        if (nx, ny) in set(res_list):
            value = 10**12
        else:
            # Closer to some resource is good; also slight preference toward opponent being further from those resources
            md = min(steps(nx, ny, rx, ry) for rx, ry in res_list)
            value = local_best + (50 - md)

        if value > best_val:
            best_val = value
            best_move = (dx, dy)

    dx, dy = best_move
    nx, ny = sx + dx, sy + dy
    if valid(nx, ny):
        return [dx, dy]
    return [0, 0]