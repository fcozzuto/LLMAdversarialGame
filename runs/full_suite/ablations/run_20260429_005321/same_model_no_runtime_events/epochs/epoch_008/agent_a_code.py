def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        return max(abs(x1 - x2), abs(y1 - y2))

    resources = observation.get("resources") or []
    live_resources = [(rx, ry) for (rx, ry) in resources if not ((rx, ry) in obs)]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    # If no resources: drift to a deterministically chosen strategic point (center-ish).
    if not live_resources:
        tx, ty = (w // 2), (h // 2)
        best = None
        for dx, dy, nx, ny in legal:
            key = (-cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key > best:
                best = key
        return [best[2], best[3]]

    # Race heuristic: prefer moves that create the largest "time advantage" to a resource,
    # while discouraging moving into opponent proximity/obvious collision.
    # Also pick the opponent's most contested resource to divert to another when tied.
    def best_resource_for(x, y):
        best_key = None
        best_r = None
        for rx, ry in live_resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # primary: our earlier arrival, then margin, then distance, then stable coordinate tiebreak
            key = (do - ds, -ds, -do, -rx, -ry)
            if best_key is None or key > best_key:
                best_key, best_r = key, (rx, ry)
        return best_r, best_key

    opp_contested, _ = best_resource_for(ox, oy)

    best_move = None
    for dx, dy, nx, ny in legal:
        # Immediate goal: maximize advantage to the best resource from next position
        our_r, our_key = best_resource_for(nx, ny)
        if our_r is None:
            continue
        # diversion: if opponent is heavily contesting same resource, prefer alternatives
        contest_same = 1 if (opp_contested is not None and our_r == opp_contested) else 0

        # proximity penalty to reduce being "in the same race lane" too easily
        prox = cheb(nx, ny, ox, oy)

        # also discourage stepping closer when we don't improve race margin
        do = cheb(ox, oy, our_r[0], our_r[1])
        ds = cheb(nx, ny, our_r[0], our_r[1])
        curr_ds = cheb(sx, sy, our_r[0], our_r[1])
        improved = 1 if ds < curr_ds else 0

        # Composite key (bigger is better). Strongly prioritize race advantage.
        key = (
            our_key[0],          # (do-ds)
            improved,           # prefer improving our distance
            -prox,              # prefer being farther from opponent
            -contest_same,      # prefer diverting if tied contest
            -ds,                # then closer ourselves
            -do,                # then farther from opponent
            -nx, -ny, dx, dy
        )
        if best_move is None or key > best_move[0]:
            best_move = (key, dx, dy)

    return [best_move[1], best_move[2]]