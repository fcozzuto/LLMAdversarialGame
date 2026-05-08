def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        return [0, 0]

    # Prefer resources on/near our side of the board relative to opponent to counter row sweeping
    def side_score(px, py):
        # closer to opponent's corner means worse (we want to "steal" remaining interior)
        return abs(px - ox) + abs(py - oy)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Evaluate each move by (1) best relative advantage after move, (2) reducing opponent's best advantage
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = int(sx + dx), int(sy + dy)
        if not in_bounds(nx, ny):
            continue

        adv_self = None
        adv_opp = None
        for rx, ry in res:
            s_d = abs(rx - nx) + abs(ry - ny)
            o_d = abs(rx - ox) + abs(ry - oy)
            rel = o_d - s_d  # positive is good
            # mild preference to interior/less "reachable by opponent cornering"
            rel -= 0.1 * (side_score(rx, ry) / (w + h))
            if adv_self is None or rel > adv_self:
                adv_self = rel
            if adv_opp is None or (-rel) > adv_opp:
                adv_opp = -rel

        # If we can't grab anything quickly, still prefer moves that reduce opponent's advantage
        # Tie-break deterministically by closer to some resource we are likely to take.
        closest = None
        for rx, ry in res:
            d = abs(rx - nx) + abs(ry - ny)
            if closest is None or d < closest[0]:
                closest = (d, rx, ry)
        opp_close = min(abs(rx - ox) + abs(ry - oy) for rx, ry in res)
        val = (adv_self, -opp_close, -closest[0])
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]