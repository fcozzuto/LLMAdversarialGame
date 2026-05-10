def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_move_towards(tx, ty):
        best = [0, 0]
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d1 = man(nx, ny, tx, ty)
            d2 = man(ox, oy, tx, ty)
            # Strongly prefer reducing our distance; slight preference to keep opponent farther.
            key = (d1, d2, abs(nx - tx) + abs(ny - ty), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        return best

    # Target choice: favor resources where we are closer than opponent (negative lead).
    # Tie-break: overall closeness, then lower coordinate for determinism.
    best_target = None
    best_key = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        lead = ds - do  # smaller is better (more lead for us)
        key = (lead, ds, ry, rx)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # If opponent is much closer to their nearest resource, "intercept" by moving towards our best steal
    # endpoint: the point adjacent to that target that we can reach quickest.
    # Heuristic: if opponent lead is big against us, prioritize blocking their nearest resource.
    opp_resources = resources
    opp_nearest = min(opp_resources, key=lambda p: man(ox, oy, p[0], p[1]))
    nxr, nyr = opp_nearest
    my_to_opp = man(sx, sy, nxr, nyr)
    opp_to_opp = man(ox, oy, nxr, nyr)
    if opp_to_opp <= my_to_opp - 3:
        # Move towards a neighbor of the opponent's nearest resource (including the cell itself).
        block_candidates = [(nxr, nyr)]
        for dx, dy in moves:
            x, y = nxr + dx, nyr + dy
            if valid(x, y):
                block_candidates.append((x, y))
        target2 = min(block_candidates, key=lambda p: (man(sx, sy, p[0], p[1]), p[1], p[0]))
        return best_move_towards(target2[0], target2[1])

    return best_move_towards(tx, ty)