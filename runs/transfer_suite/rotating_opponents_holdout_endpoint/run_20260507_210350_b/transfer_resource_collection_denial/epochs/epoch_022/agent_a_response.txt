def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    rlist = [tuple(p) for p in resources]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        me = (nx, ny)

        # Evaluate after this move: prefer a resource we can reach no later than opponent.
        # Secondary: prefer smaller distance gap; tertiary: progress toward nearest resource.
        val = -10**18
        nearest = 10**9
        gap_best = -10**18
        for tr in rlist:
            dme = man(me, tr)
            dob = man((ox, oy), tr)
            if dme <= dob:
                gap = dob - dme  # bigger means more secure
                cand = 1000000 + gap * 100 - dme
                if cand > val:
                    val = cand
                    gap_best = gap
            nearest = min(nearest, dme)

        # If we cannot "secure" any resource this turn, still move toward one while
        # trying to reduce opponent's advantage (minimize their lead on the best target).
        if val == -10**18:
            lead_best = 10**9
            for tr in rlist:
                dme = man(me, tr)
                dob = man((ox, oy), tr)
                lead = dob - dme
                if lead < lead_best:
                    lead_best = lead
            val = 50000 - lead_best * 50 - nearest

        # Tiny deterministic tie-break: closer to opponent is slightly worse (avoid accidental swap).
        val -= man(me, (ox, oy)) * 0.01

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]