def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Precompute for speed: resources list of tuples
    res = [(r[0], r[1]) for r in resources]

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h) or blocked(nx, ny):
            nx, ny = x, y  # deterministic fallback to staying in place
        # Resource race: favor positions that are closer than opponent to some resource,
        # strongly if we are ahead, then slightly by overall closeness.
        best_lead = -10**9
        best_dme = 10**9
        best_dopp = 10**9
        for tx, ty in res:
            d_me = abs(tx - nx) + abs(ty - ny)
            d_opp = abs(tx - ox) + abs(ty - oy)
            lead = d_opp - d_me
            if lead > best_lead or (lead == best_lead and d_me < best_dme):
                best_lead = lead
                best_dme = d_me
                best_dopp = d_opp

        # Also add a small term to reduce getting closer to opponent's current position
        # while still allowing pursuit via resources.
        opp_dist = abs(nx - ox) + abs(ny - oy)
        val = (best_lead * 1000) - best_dme + (best_dopp * 0.01) + (opp_dist * 0.001)

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]