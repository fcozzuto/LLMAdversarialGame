def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obs.add((p[0], p[1]))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            rx, ry = r[0], r[1]
            if (rx, ry) not in obs:
                resources.append((rx, ry))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    moves = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if inside(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # If no resources visible, head to opponent-opposite corner deterministically.
    if not resources:
        target = (w - 1 - ox, h - 1 - oy)
        best = None
        for dx, dy, nx, ny in sorted(moves, key=lambda t: (t[0], t[1])):
            score = man(nx, ny, target[0], target[1])
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Evaluate moves by local 1-step lookahead over best target to compete for.
    def eval_state(sx, sy):
        best = None
        for rx, ry in resources:
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            # Favor picking/contesting nearer resources where we beat opponent in distance.
            # Also slight preference for high ds improvements by adding inverse of ds.
            win_term = (do - ds)  # positive if we are closer
            denom = ds + 1
            score = -win_term * 10 + denom + (rx * 0 + ry * 0)  # deterministic base
            if best is None or score < best:
                best = score
        return best if best is not None else 10**9

    best = None
    for dx, dy, nx, ny in sorted(moves, key=lambda t: (t[0], t[1], t[2], t[3])):
        # Assume opponent moves next; incorporate a conservative penalty: if opponent is already closer to our
        # best target, reduce attractiveness.
        cur_score = eval_state(nx, ny)

        # Conservative opponent-closer penalty: compare our best reachable contest vs their current best.
        opp_best = None
        for rx, ry in resources:
            do = man(ox, oy, rx, ry)
            if opp_best is None or do < opp_best:
                opp_best = do
        # Reduce score if we are not significantly closer than opponent.
        # Compute our closest distance to any resource.
        our_best = None
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            if our_best is None or ds < our_best:
                our_best = ds
        if opp_best is not None and our_best is not None:
            cur_score += (our_best - opp_best) * 3

        if best is None or cur_score < best[0]:
            best = (cur_score, dx, dy)

    return [best[1], best[2]]