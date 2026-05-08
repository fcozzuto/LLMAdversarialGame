def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2}

    unclaimed = observation.get("unclaimed_cells", []) or []
    un = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) == 2}

    self_terr = observation.get("self_territory", []) or []
    st = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) == 2}
    opp_terr = observation.get("opponent_territory", []) or []
    ot = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) == 2}

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (float("-inf"), 0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue

        d_center = man(nx, ny, cx, cy)
        d_opp = man(nx, ny, ox, oy)
        value = 0.0

        if (nx, ny) in un:
            value += 3.2
        elif (nx, ny) in ot:
            value += 2.1
        elif (nx, ny) in st:
            value += 0.4

        # Prefer pushing into the unknown while pressuring toward opponent.
        value += -0.03 * d_center
        value += 0.035 * (-d_opp)  # closer to opponent is better

        # Slightly discourage stepping next to obstacles (except center-crossing).
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obs:
                    near_obs += 1
        value -= 0.02 * near_obs

        # Deterministic tie-break: smaller dx, then smaller dy, then stay of preference by ordering.
        cand = (value, -dx, -dy)
        if cand > (best[0], -best[1], -best[2]):
            best = (value, dx, dy)

    if best[0] == float("-inf"):
        return [0, 0]
    return [best[1], best[2]]