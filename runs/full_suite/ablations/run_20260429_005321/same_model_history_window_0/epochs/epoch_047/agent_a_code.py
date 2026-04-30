def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # If no resources, drift toward opponent's side while avoiding obstacles
    if not resources:
        best = None
        bestv = -10**18
        target = (w-1-sx, h-1-sy)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -dist((nx, ny), target)
            if v > bestv or (v == bestv and (dx, dy) == (-1,-1)):
                bestv = v
                best = [dx, dy]
        return best if best is not None else [0, 0]

    # Competitive targeting: maximize (opponent advantage reduction) after the move
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate by the best resource for us from this hypothetical position
        my_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist((nx, ny), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources we can reach before them; add slight tie-break for shorter ds
            val = (do - ds) * 10 - ds
            if val > my_best:
                my_best = val

        # Small preference for staying out of bad parity with opponent direction
        # (deterministic, but materially changes behavior)
        step_to_opp = dist((nx, ny), (ox, oy))
        val_total = my_best - 0.05 * step_to_opp

        if val_total > best_val:
            best_val = val_total
            best_move = [dx, dy]

    # If all candidate moves were invalid, stay
    if best_move == [0, 0] and (sx, sy) in obstacles:
        return [0, 0]
    return best_move