def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if in_bounds(nx, ny) and (nx, ny) not in obs:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        # Deterministically drift toward center while also slightly reducing opponent's mobility.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in valid:
            val = (man(nx, ny, cx, cy) * -2) + (man(nx, ny, ox, oy) * 1)
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # Contest the resource the opponent is currently closest to; if we are already closer, move to steal a different one.
    # Score combines: relative advantage, and "pressure" for contested resources (opponent closer => higher weight).
    best = None
    for dx, dy, nx, ny in valid:
        rel_best = -10**9
        for rx, ry in resources:
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            if opp_d < 1:
                opp_d = 1
            # pressure: if opponent is closer than us, strongly increase weight
            my_curr = man(x, y, rx, ry)
            rel = (opp_d - my_d)
            steal_bonus = 0
            if man(nx, ny, rx, ry) <= man(x, y, rx, ry):
                steal_bonus = 0.25  # encourage progress toward a target
            pressure = 1.0 + max(0, (opp_d - my_curr) / 3.0)  # contested => larger
            # also prefer moving toward near resources (helps prevent dithering)
            near_pref = -0.08 * my_d
            val = pressure * rel + steal_bonus + near_pref
            if val > rel_best:
                rel_best = val
        # Add slight tie-break toward keeping distance from opponent (avoid herding into their route)
        val2 = rel_best - 0.02 * man(nx, ny, ox, oy)
        if best is None or val2 > best[0]:
            best = (val2, dx, dy)

    return [best[1], best[2]]