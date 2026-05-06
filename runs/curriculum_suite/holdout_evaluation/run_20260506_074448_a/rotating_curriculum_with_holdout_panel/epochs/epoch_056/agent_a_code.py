def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0
    def center_bias(x, y):
        dx = x - cx0
        dy = y - cy0
        return -0.02 * (dx * dx + dy * dy)

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    # If no resources, drift toward center to avoid falling behind.
    if not resources:
        best = [0, 0]
        best_sc = -10**18
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            sc = center_bias(nx, ny)
            if sc > best_sc:
                best_sc = sc
                best = [dx, dy]
        return best

    # Resource_denier adaptation: prefer moves that make us closer than the opponent on high-value contested resources.
    best = [0, 0]
    best_sc = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            oppd = man(ox, oy, rx, ry)

            # "Contest edge": big when we are closer than opponent; also reward reducing our distance.
            # Scale oppd-myd so denying targets where opponent is closer (negative contest) gets less preference.
            edge = (oppd - myd)
            sc_r = 80.0 * edge / (1.0 + myd) - 0.5 * myd

            if sc_r > my_best:
                my_best = sc_r

        # Small tiebreak: reduce distance to nearest resource overall and slight center pull.
        nearest = min(man(nx, ny, rx, ry) for rx, ry in resources if (rx, ry) not in obstacles)
        sc = my_best - 0.2 * nearest + center_bias(nx, ny)

        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best