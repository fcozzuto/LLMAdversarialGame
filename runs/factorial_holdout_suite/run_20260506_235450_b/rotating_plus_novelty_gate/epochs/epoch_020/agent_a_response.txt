def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_dx, best_dy = 0, 0
    best_val = None

    # Baseline opponent pressure: which resource they are closest to.
    opp_best = None
    opp_best_d = 10**9
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if d < opp_best_d:
            opp_best_d = d
            opp_best = (rx, ry)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        val = -10**18
        # Evaluate by best resource swing plus keeping ourselves generally closer.
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            swing = opd - myd  # higher is better: we are closer than opponent
            close_bonus = 0
            if myd == 0:
                close_bonus += 50
            # If opponent is denier for a particular resource, counter it deterministically.
            denier_focus = 0
            if opp_best == (rx, ry) and opd < myd:
                denier_focus = 20
            # Tie-break preference: fewer steps to any resource.
            overall = swing * 10 + close_bonus + denier_focus - myd * 0.3
            if overall > val:
                val = overall

        # Mild preference to reduce distance to opponent if no strong resource swing.
        if val < 0 and (man(nx, ny, ox, oy) < man(sx, sy, ox, oy)):
            val += 3

        if best_val is None or val > best_val:
            best_val = val
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]