def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if ok(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            score = (man(nx, ny, ox, oy), -man(nx, ny, cx, cy))
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    res_list = [(r[0], r[1]) for r in resources]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles:
            continue

        # Prefer immediate collection, then win-by-closer, then reach speed.
        immediate = 1 if (nx, ny) in set(res_list) else 0

        best_gain = -10**9
        best_self = 10**9
        best_opp = 10**9
        for rx, ry in res_list:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Positive if we are closer than opponent for that resource
            gain = od - sd
            if gain > best_gain or (gain == best_gain and (sd < best_self or (sd == best_self and od < best_opp))):
                best_gain, best_self, best_opp = gain, sd, od

        # Make opponent-farming less attractive: penalize moves that keep opponent also very close.
        opp_pressure = min(man(nx, ny, rx, ry) - man(ox, oy, rx, ry) for rx, ry in res_list)
        score = (
            -immediate,              # immediate collection first
            -(best_gain),            # maximize being closer
            best_self,               # then minimize distance to that target
            opp_pressure,           # then prefer not to be "equally bad" for opponent
            nx, ny                    # tie-break deterministically
        )
        if best is None or score < best[0]:
            best = (score, dx, dy)

    return [best[1], best[2]]