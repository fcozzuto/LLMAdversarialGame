def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2)

    resources = observation.get("resources", []) or []
    res = [(p[0], p[1]) for p in resources if isinstance(p, (list, tuple)) and len(p) >= 2]
    resset = set(res)

    if (sx, sy) in resset:
        return [0, 0]
    if not res:
        return [0, 0]

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Target: maximize distance advantage to get there first.
    best_t = None
    best_adv = None
    for rx, ry in res:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        adv = od - sd
        if best_adv is None or adv > best_adv or (adv == best_adv and sd < dist(sx, sy, best_t[0], best_t[1])):
            best_adv = adv
            best_t = (rx, ry)

    tx, ty = best_t

    # If we are not closer than opponent, also try to reduce their next best threat by blocking-like move:
    # deterministically pick step that minimizes (our_dist, opp_dist_to_target_min) lexicographically.
    # Also take the move if it lands on a resource.
    best_move = (0, 0)
    best_key = None
    for mdx, mdy in legal:
        nx, ny = sx + mdx, sy + mdy
        if (nx, ny) in resset:
            return [mdx, mdy]
        our_d = dist(nx, ny, tx, ty)

        # Opponent pressure: estimate their distance to the chosen target after our move (unchanged position),
        # but include distance to the closest resource to encourage locking.
        opp_min = None
        for rx, ry in res:
            d = dist(ox, oy, rx, ry)
            if opp_min is None or d < opp_min:
                opp_min = d

        # Key favors: our_d then (opp_min - our_d) then deterministic tiebreak on move.
        key = (our_d, -(opp_min - our_d), mdx, mdy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]