def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    adj8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    moves = adj8 + [(0, 0)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obs_adj(x, y):
        p = 0
        for dx, dy in adj8:
            if (x + dx, y + dy) in obstacles:
                p += 1
        return p

    if not resources:
        targets = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(targets, key=lambda t: (man(sx, sy, t[0], t[1]) - man(ox, oy, t[0], t[1]), -t[0], -t[1]))
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for mdx, mdy in moves:
            if valid(sx + mdx, sy + mdy):
                return [mdx, mdy]
        return [0, 0]

    # Pick a resource where we are currently advantaged (or least behind).
    best = None
    best_key = None
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer larger advantage (opd - myd). Tie-break by smaller myd.
        key = (opd - myd, -myd, rx + ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # Evaluate moves with a 1-step lookahead for our advantage on the chosen target.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if (nx, ny) == (tx, ty):
            return [dx, dy]
        myd1 = man(nx, ny, tx, ty)
        opd1 = man(ox, oy, tx, ty)
        # If we move closer, we want opponent unchanged; if we move away, avoid.
        adv = (opd1 - myd1)
        val = 2.5 * adv - 0.6 * abs(ny - sy) - 0.9 * obs_adj(nx, ny)

        # Mild contention check: discourage moves that bring us into cells adjacent to obstacles
        # without improving advantage.
        if adv < (opd1 - man(sx, sy, tx, ty)):
            val -= 0.4

        # Secondary tie-break: keep moving generally toward target; deterministic by coordinates.
        val += -0.05 * myd1 - 0.0001 * (nx * 9 + ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]