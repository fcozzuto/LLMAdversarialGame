def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles if len(p) >= 2)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Filter reachable/valid resources
    res = []
    for r in resources:
        if len(r) >= 2:
            rx, ry = r[0], r[1]
            if inb(rx, ry) and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res or (sx, sy) in obs:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break order preference (prefer movement over stay)
    pref = {(dx, dy): (0 if (dx, dy) != (0, 0) else 1) for dx, dy in moves}

    best = None
    best_move = (0, 0)

    # Score candidate move using best contested resource under a 1-step lookahead
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_d = None
        opp_d = None
        best_margin = None
        # Evaluate against resources: prefer increasing (opp_dist - my_dist) and reducing my_dist
        for rx, ry in res:
            dself = man((nx, ny), (rx, ry))
            dopp = man((ox, oy), (rx, ry))
            # margin after move; also reward being extremely close (likely collection soon)
            margin = dopp - dself
            val = (margin, -dself, -dopp)
            if best_margin is None or val > best_margin:
                best_margin = val
                my_d = dself
                opp_d = dopp

        # If we can collect immediately, strongly prefer it
        collect_now = 1 if any((nx, ny) == r for r in res) else 0
        if collect_now:
            score = (10, best_margin[0], best_margin[1], best_margin[2], -pref[(dx, dy)])
        else:
            score = (0, best_margin[0], best_margin[1], best_margin[2], -pref[(dx, dy)])

        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]