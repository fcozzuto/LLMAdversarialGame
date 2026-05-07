def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0)) or (0, 0)
    ox, oy = observation.get("opponent_position", (0, 0)) or (0, 0)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = p[0], p[1]
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))

    if not res:
        return [0, 0]

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    # Pick best contest target: maximize (opp_dist - our_dist), prefer closer resources
    best_r = None
    best_key = (-10**9, -10**9)
    for r in res:
        du = md((sx, sy), r)
        do = md((ox, oy), r)
        key1 = do - du
        key2 = -du
        if key1 > best_key[0] or (key1 == best_key[0] and key2 > best_key[1]):
            best_key = (key1, key2)
            best_r = r

    tr = best_r
    if tr is None:
        return [0, 0]

    # Evaluate moves by improving our distance to target while also reducing/contesting opponent progress
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in legal:
        nu = (sx + dx, sy + dy)
        du = md(nu, tr)
        do = md((ox, oy), tr)  # our move doesn't move opponent; still influences tie by being closer/earlier next turn
        # Secondary: head off opponent stealing by choosing a move that makes their best alternative farther.
        alt_pen = 0
        # compute quick approx of how many resources opponent can reach sooner than us (small sample)
        # use up to 4 closest resources to opponent
        opp_sorted = sorted(res, key=lambda r: md((ox, oy), r))[:4]
        for r in opp_sorted:
            du2 = md(nu, r)
            do2 = md((ox, oy), r)
            if do2 < du2:  # opponent lead remains
                alt_pen += (du2 - do2)
        # If we can step onto a resource, prioritize heavily
        hit = 1 if nu == tr else 0
        val = hit * 100000 + (best_key[0]) * 0.1 + (-du) * 10 + (du - do) * 2 - alt_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]