def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        dy = by - ay
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if w <= 0 or h <= 0:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Choose the move that maximizes guaranteed grabbing odds: prefer resources where we can arrive no later than opponent,
    # otherwise block by moving closer to the most competitive resource.
    best = (0, 0)
    best_val = -10**18
    eps = 1e-9

    for mdx, mdy in moves:
        nsx, nsy = sx + mdx, sy + mdy
        if not inb(nsx, nsy):
            continue
        val = 0.0

        # Immediate resource pick preference
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            if nsx == rx and nsy == ry:
                val += 1e6

        # Evaluate competitive resources
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            self_d = cheb(nsx, nsy, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)

            # If we are at least as fast, heavily prefer.
            if self_d <= opp_d:
                val += 2000.0 / (1.0 + self_d) + 20.0 * (opp_d - self_d)
            else:
                # Otherwise reduce value, but still push toward the most race-winning target.
                val -= 50.0 * (self_d - opp_d) + 5.0 / (1.0 + self_d)

        # Small tie-break: keep farther from opponent to reduce their effective races
        val += 0.1 * cheb(nsx, nsy, ox, oy)

        # Deterministic tie-break: prefer staying if equal, else order by move list
        if val > best_val + eps:
            best_val = val
            best = (mdx, mdy)

    return [int(best[0]), int(best[1])]