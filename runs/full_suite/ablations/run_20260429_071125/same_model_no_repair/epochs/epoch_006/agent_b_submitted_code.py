def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    occ = set((p[0], p[1]) for p in obstacles)
    res_set = set((r[0], r[1]) for r in resources)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my = (sx, sy)
    opp = (ox, oy)

    # Target: resource where we are relatively closer than opponent.
    if resources:
        best_r = resources[0]
        best_val = -10**18
        for rx, ry in resources:
            r = (rx, ry)
            ds = man(my, r)
            do = man(opp, r)
            # Big bonus for immediate pick
            pick_bias = 1e6 if r == my else 0
            # Slight preference for more central cells to reduce cornering
            cb = -0.02 * (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
            # Primary: opponent advantage (larger means we are closer)
            val = (do - ds) + cb + pick_bias
            # Tie-breaker: prefer closer resources
            if val > best_val or (val == best_val and ds < man(my, best_r)):
                best_val = val
                best_r = r
        tx, ty = best_r
    else:
        tx, ty = (w - 1) / 2, (h - 1) / 2

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        # Avoid moving onto opponent (engine would keep us, but keep score safe)
        if (nx, ny) == (ox, oy):
            continue

        new = (nx, ny)
        # Immediate resource capture
        if new in res_set:
            score = 10**9
        else:
            # Advantage on current best target
            d_before = man(my, (tx, ty)) if resources else man(my, (tx, ty))
            d_after = man(new, (tx, ty)) if resources else man(new, (tx, ty))
            improve = d_before - d_after

            # Make it harder for opponent to grab our next target: reduce our distance gap vs opp.
            if resources:
                # Use best resource by our heuristic, re-evaluate quickly among top few by our local distances.
                # Deterministic: just compute over all resources but keep formula cheap.
                gap_now = None
                gap_after = None
                for rx, ry in resources:
                    r = (rx, ry)
                    ds1 = man(my, r)
                    do1 = man(opp, r)
                    ds2 = man(new, r)
                    do2 = man(opp, r)
                    g1 = do1 - ds1
                    g2 = do2 - ds2
                    # We only care about max gap; compute maxima
                    if gap_now is None or g1 > gap_now:
                        gap_now = g1
                    if gap_after is None or g2 > gap_after:
                        gap_after = g2
            else:
                gap_now = 0
                gap_after = 0

            # Additional terms: keep distance from opponent while moving toward target
            opp_dist = man(new, opp)
            toward = -(abs(nx - tx) + abs(ny - ty)) if resources else -(abs(nx - tx) + abs(ny - ty))
            score = (2000 * improve) + (50 * (gap_after - gap_now)) + (0.8 * opp_dist) + (2.0 * toward)

        # Deterministic tie-break: prefer staying if equal, then lexicographically smallest delta
        if score > best_score or (score == best_score and (dx, dy) == (0, 0)) or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]