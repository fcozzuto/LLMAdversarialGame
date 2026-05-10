def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    resources = [tuple(r) for r in observation.get("resources", []) if 0 <= r[0] < w and 0 <= r[1] < h and tuple(r) not in obstacles]
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    me = (sx, sy)
    opp = (ox, oy)

    threatened = [r for r in resources if man(r, opp) == 1]
    if threatened:
        # Deterministically choose the threatened resource that is "closest to us" (to respond quickly)
        tr = min(threatened, key=lambda r: (man(r, me), r[0], r[1]))
        best = (0, 0)
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man((nx, ny), tr)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    # Main: choose move that maximizes immediate capture potential, then race advantage
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        pos = (nx, ny)

        # If we can pick up immediately, always do it
        if pos in obstacles:
            continue
        if pos in set(resources):
            return [dx, dy]

        # Evaluate best resource under this hypothetical position
        best_r_val = None
        for r in resources:
            sd = man(pos, r)
            od = man(opp, r)

            # Prefer guaranteed leads; otherwise prefer smallest sd, then largest separation
            # Lead if we arrive strictly sooner or same but opponent not one step away
            lead = (sd < od)
            eq = (sd == od)
            immediate_opp_take = (od == 0 or od == 1)

            val = (1 if lead else 0, 1 if (eq and not immediate_opp_take) else 0, -sd, od - sd, -r[1], -r[0])
            if best_r_val is None or val > best_r_val:
                best_r_val = val

        # Secondary: avoid moving closer to opponent if we don't have a lead
        move_to_opp = man(pos, opp)
        opp_dist_score = (-move_to_opp, dx == 0 and dy == 0)
        overall = (best_r_val, opp_dist_score)
        if best_val is None or overall > best_val:
            best_val = overall
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]