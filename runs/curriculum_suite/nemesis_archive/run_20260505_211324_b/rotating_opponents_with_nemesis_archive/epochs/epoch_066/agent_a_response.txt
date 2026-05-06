def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = (-(10**9), 0, 0)
    best_move = (0, 0)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not res:
        # deterministic fallback: drift toward center while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                d = man(nx, ny, cx, cy)
                key = (-d, dx, dy)
                if key > best:
                    best, best_move = key, (dx, dy)
        return [best_move[0], best_move[1]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        # Prefer a move that makes us significantly closer to a resource than the opponent,
        # while also keeping our own distance small.
        best_adv = -(10**9)
        best_my = 10**9
        for rx, ry in res:
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - my_d
            if adv > best_adv or (adv == best_adv and my_d < best_my):
                best_adv = adv
                best_my = my_d
        # Tie-break: prefer staying closer to opponent less (reduces their interception) and then deterministically.
        opp_gap = man(nx, ny, ox, oy)
        key = (best_adv, -best_my, -opp_gap)
        if key > best:
            best = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]