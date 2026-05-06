def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    def obstacle_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if (nx, ny) in blocked:
                    p += 1
        return p

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            if legal(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if not targets:
        bx, by = sx, sy
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            val = -(obstacle_pen(nx, ny))
            t = (val, -abs(nx - ox) - abs(ny - oy), -(abs(dx) + abs(dy)))
            if t > best:
                best, bx, by = t, nx, ny
        return [bx - sx, by - sy]

    best_t = (-10**18, 0, 0)
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        my_d_to_best = 10**9
        opp_d_to_best = 10**9
        lead = -10**9
        for tx, ty in targets:
            sd = abs(tx - nx) + abs(ty - ny)
            od = abs(tx - ox) + abs(ty - oy)
            if sd < my_d_to_best:
                my_d_to_best = sd
            if od < opp_d_to_best:
                opp_d_to_best = od
            dlead = od - sd  # positive means we are closer than opponent
            if dlead > lead:
                lead = dlead
        # Prefer strong lead; also keep reasonable distance to avoid wandering.
        val = (lead * 100) - (my_d_to_best * 2) + (opp_d_to_best * 0.5) - (obstacle_pen(nx, ny) * 3)
        # Tie-break deterministically: closer to center-ish, then prefer advancing towards resources (lower dx,dy lex).
        center = abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)
        t = (val, -my_d_to_best, -lead, -center, -abs(dx) - abs(dy), dx, dy)
        if t > best_t:
            best_t = t
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]