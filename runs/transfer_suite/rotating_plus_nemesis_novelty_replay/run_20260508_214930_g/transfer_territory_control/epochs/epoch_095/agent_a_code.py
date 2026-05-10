def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_t = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_t = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Build a small deterministic "frontier" from our territory: target unclaimed/opp adjacent to our cells.
    frontier = []
    for (x, y) in self_t:
        for dx, dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)):
            nx, ny = x + dx, y + dy
            if ok(nx, ny) and (nx, ny) in (unclaimed | opp_t):
                frontier.append((nx, ny))
    # If no frontier (early), fallback to unclaimed then to opponent territory.
    if not frontier:
        if unclaimed:
            frontier = list(unclaimed)
        elif opp_t:
            frontier = list(opp_t)
        else:
            frontier = [(ox, oy)]

    # Deterministic tie-breaking: prefer higher value, then lower distance, then lexicographic.
    def cell_value(x, y):
        v = 0
        if (x, y) in opp_t: v += 500  # strong flip
        if (x, y) in unclaimed: v += 70
        if (x, y) in self_t: v -= 20  # avoid wasting step on already-owned if possible
        # Safety: prefer moves that keep some distance from opponent (unless targeting opp cell directly).
        d_to_opp = abs(x - ox) + abs(y - oy)
        if (x, y) not in opp_t:
            v += min(30, d_to_opp)  # farther is safer
        else:
            v -= max(0, 10 - d_to_opp)  # still ok but reduce suicide
        # Slight preference to increase our expansion direction relative to opponent.
        v += (abs(x - ox) - abs(sx - ox)) * 2 + (abs(y - oy) - abs(sy - oy))
        return v

    best_move = (0, 0)
    best_score = -10**18

    # Evaluate each immediate move by "best achievable target" among the frontier.
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue
        # Move effect: value target minus distance from the new position.
        local_best = -10**18
        for tx, ty in frontier:
            if (tx, ty) in obstacles:
                continue
            tv = cell_value(tx, ty)
            d = abs(tx - nx) + abs(ty - ny)
            score = tv - d * 3
            if score > local_best:
                local_best = score
        # Encourage direct captures if possible this step.
        if (nx, ny) in opp_t:
            local_best += 250
        if (nx, ny) in unclaimed:
            local_best += 25
        # Discourage stepping back into our own territory unless it improves capture prospects.
        if (nx, ny) in self_t:
            local_best -= 5
        # Mild tie-breaker: smaller distance to opponent reduces being out-tempoed when contesting.
        local_best -= (abs(nx - ox) + abs(ny - oy)) * 0.05

        if local_best > best_score or (local_best == best_score and (ddx, ddy) < best_move):
            best_score = local_best
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]