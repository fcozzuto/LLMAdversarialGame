def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation["grid_width"]
    h = observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    # Filter out resources on obstacles (shouldn't exist, but be safe)
    res = [(rx, ry) for rx, ry in resources if (rx, ry) not in obs]
    if not res:
        return [0, 0]

    # Greedy evaluation of next position vs best reachable resource contest
    best = (-(10**18), 0, 0)  # (value, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        # Look for the resource where we'd have the strongest relative advantage after this move.
        # Positive advantage means we are closer than opponent.
        val = -(10**18)
        for i, (rx, ry) in enumerate(res):
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Immediate grab gets huge value; otherwise prefer positive (opd-myd),
            # then closer overall; deterministic tie by resource index and coords.
            if myd == 0:
                cur = 10**9 - i
            else:
                adv = opd - myd
                cur = (adv * 10**4) - (myd * 3) - (0 if adv > 0 else 1) * (myd // 2) - i
                # Small deterministic bias to stabilize: prefer smaller coords if still tied.
                cur -= rx * 0.01 + ry * 0.001
            if cur > val:
                val = cur

        # Secondary: reduce risk of letting opponent immediately grab by staying near the closest contested resource.
        # (Uses our current position as a simple deterministic regularizer.)
        # Prefer moving that decreases our distance to opponent's closest resource.
        opp_best = 10**18
        for (rx, ry) in res:
            opp_best = min(opp_best, cheb(ox, oy, rx, ry))
        my_to_opp = cheb(nx, ny, ox, oy)
        val -= my_to_opp * 0.1

        if val > best[0]:
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]