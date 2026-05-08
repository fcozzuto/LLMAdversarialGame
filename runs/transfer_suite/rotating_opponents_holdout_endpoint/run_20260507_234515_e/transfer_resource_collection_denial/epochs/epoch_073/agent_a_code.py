def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def cheb(a, b, c, d):
        da, db = abs(a-c), abs(b-d)
        return da if da > db else db

    best_move = (0, 0)
    best_val = None
    # If opponent is closer to a resource, we may want to steal another; evaluate per-move advantage.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate how good our next step is against opponent over all resources (best we can aim for next).
        # Key: prioritize maximizing (opp_dist - self_dist), then prefer fewer self steps, then closer to center-ish.
        best_adv_for_this = None
        for rx, ry in res:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # higher => more likely we arrive first
            # small tie-breakers to reduce dithering deterministically
            tie = (adv, -ds, -abs((rx - (w-1)/2)) - abs((ry - (h-1)/2)), -rx, -ry)
            if best_adv_for_this is None or tie > best_adv_for_this:
                best_adv_for_this = tie

        if best_val is None or best_adv_for_this > best_val:
            best_val = best_adv_for_this
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]