def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles if len(p) >= 2)
    resset = set((p[0], p[1]) for p in resources if len(p) >= 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def absd(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If standing on a resource, prioritize staying (deterministic collection).
    if (sx, sy) in resset:
        return [0, 0]

    # Pick a target resource based on which we can reach first (tie-break-friendly).
    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obst:
            continue
        ourd = absd(sx, sy, rx, ry)
        oppd = absd(ox, oy, rx, ry)
        # Prefer resources we are strictly closer to; otherwise prefer those with largest oppd-ourd.
        key = (0 if ourd <= oppd else 1, -(oppd - ourd), ourd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    best_move = [0, 0]
    best_eval = None

    # Evaluate each candidate move with "win-first" pressure toward target and away from opponent-favored resources.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        our_to_target = absd(nx, ny, tx, ty)
        opp_to_target = absd(ox, oy, tx, ty)

        # If target is already adjacent/at, encourage capture by moving closer.
        # Also compute overall advantage across all resources to avoid walking into opponent wins.
        adv_sum = 0
        adv_min = 10**9
        opp_adv_min = 10**9
        for rx, ry in resources:
            if (rx, ry) in obst:
                continue
            ourd = absd(nx, ny, rx, ry)
            oppd = absd(ox, oy, rx, ry)
            diff = oppd - ourd  # higher means we are closer than opponent
            adv_sum += diff
            if ourd < adv_min:
                adv_min = ourd
            if oppd < opp_adv_min:
                opp_adv_min = oppd

        # Multi-term deterministic evaluation.
        # - Strongly prioritize moving closer to our target.
        # - Prefer states where we are closer than opponent on average.
        # - Penalize moves that let opponent have a very near resource.
        evalv = (
            (opp_to_target - our_to_target) * 1000
            + adv_sum * 5
            - our_to_target * 2
            - (opp_adv_min) * 0.2
            - (abs(dx) + abs(dy)) * 0.05
        )

        # Tie-break deterministically: prefer smaller eval variance by closest-to-target, then lexicographic move.
        tie = (our_to_target, -adv_min, dx, dy)
        key = (evalv, -tie[0], tie[1], -tie[2], -tie[3])
        if best_eval is None or key > best_eval:
            best_eval = key
            best_move = [dx, dy]

    return best_move