def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cell_blocked(nx, ny):
        return (nx, ny) in obstacles

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    if not resources:
        dx = -sign(ox - x)
        dy = -sign(oy - y)
        return [dx, dy]

    # Deterministic target evaluation: prioritize resources where we are closer than opponent,
    # then where opponent is farther, and finally overall closeness.
    def target_value(tx, ty):
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_me  # positive means we're ahead
        # If we're behind, discourage strongly but don't ignore completely (can swing with move).
        return (lead * 1000) - d_me + (d_opp * 0.01)

    # Pick a coarse best target (deterministic).
    best_t = None
    best_tv = None
    for r in resources:
        tx, ty = r[0], r[1]
        tv = target_value(tx, ty)
        if best_tv is None or tv > best_tv:
            best_tv = tv
            best_t = (tx, ty)

    tx, ty = best_t

    # Score each immediate move by how it changes our ability to reach the chosen target
    # while also reducing risk of the opponent reaching that same target first.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or cell_blocked(nx, ny):
            continue

        d_me_new = abs(tx - nx) + abs(ty - ny)
        d_opp_here = abs(tx - ox) + abs(ty - oy)

        # Also consider immediate opportunistic switch to any resource if it becomes a better lead.
        best_lead_new = -10**9
        best_alt_d = 10**9
        for rx, ry in resources:
            d_me_alt = abs(rx - nx) + abs(ry - ny)
            d_opp_alt = abs(rx - ox) + abs(ry - oy)
            lead_alt = d_opp_alt - d_me_alt
            if lead_alt > best_lead_new or (lead_alt == best_lead_new and d_me_alt < best_alt_d):
                best_lead_new = lead_alt
                best_alt_d = d_me_alt

        # Primary: secure/extend advantage for some resource.
        # Secondary: closer to chosen target.
        score = (best_lead_new * 2000) + (d_opp_here - d_me_new) * 10 - d_me_new

        # Tie-break deterministically toward smaller dx,dy lexicographically after preferring forward pressure.
        key = (score, -abs(d_me_new), -((nx + ny) % 7), dx, dy)
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]