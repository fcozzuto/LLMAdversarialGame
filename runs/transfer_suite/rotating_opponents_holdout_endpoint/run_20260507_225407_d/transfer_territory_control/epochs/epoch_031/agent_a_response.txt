def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = to_set("obstacles")
    self_t = to_set("self_territory")
    opp_t = to_set("opponent_territory")
    un = to_set("unclaimed_cells")

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs_sorted = sorted(dirs, key=lambda d: (d[0], d[1]))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Choose a strategic target: unclaimed but "frontier" toward opponent.
    if un:
        sp = (int(sx), int(sy))
        op = (int(ox), int(oy))
        def un_score(cell):
            c = (cell[0], cell[1])
            ds = man(sp, c)
            do = man(op, c)
            # Prefer closer to us, but also closer to opponent (frontier control)
            return ds - 0.55 * do + (0.001 * (c[0] * 7 + c[1]))
        target = min(un, key=un_score)
    elif opp_t:
        sp = (int(sx), int(sy))
        target = min(opp_t, key=lambda c: man(sp, (c[0], c[1])))
    else:
        return [0, 0]

    tx, ty = int(target[0]), int(target[1])
    cur = (int(sx), int(sy))

    # One-step lookahead with obstacle avoidance; bias toward capturing opponent territory.
    best = (10**9, 10**9, None)
    for dx, dy in dirs_sorted:
        nx, ny = cur[0] + dx, cur[1] + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        dcur = abs(cur[0] - tx) + abs(cur[1] - ty)
        dnext = abs(nx - tx) + abs(ny - ty)
        into_opp = (nx, ny) in opp_t
        into_un = (nx, ny) in un
        into_self = (nx, ny) in self_t
        # primary: reduce distance; secondary: prefer flipping opponent / entering unclaimed
        primary = dnext
        secondary = (-1 if into_opp else 0) + (-0.2 if into_un else 0) + (0.05 if into_self else 0)
        # tertiary: deterministic preference ordering
        cand = (primary, secondary, (dx, dy))
        if cand < best:
            best = cand

    dx, dy = best[2]
    return [int(dx), int(dy)]