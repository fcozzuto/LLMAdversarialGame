def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    obs = set((p[0], p[1]) for p in obstacles)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def d4(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Choose target that we are most advantaged for (closer than opponent), else least bad contest.
    best_t = None
    best_key = None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    for rx, ry in resources:
        md = d4(sx, sy, rx, ry)
        od = d4(ox, oy, rx, ry)
        adv = md - od  # negative is good
        center = abs(rx - cx) + abs(ry - cy)
        key = (adv, md, center, rx, ry)
        if best_key is None or key < best_key:
            best_key, best_t = key, (rx, ry)
    tx, ty = best_t

    # Find best opponent pressure target too; we may intercept near it if opponent is clearly closer.
    press_t = None
    press_key = None
    for rx, ry in resources:
        md = d4(sx, sy, rx, ry)
        od = d4(ox, oy, rx, ry)
        # higher (od-md) means opponent advantage
        key = (-(od - md), od, rx, ry)
        if press_key is None or key < press_key:
            press_key, press_t = key, (rx, ry)
    px, py = press_t

    def step_toward(x, y, tx, ty):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return dx, dy

    # Decide whether to "defend/intercept": only if opponent is notably closer to its pressure target.
    my_p = d4(sx, sy, px, py)
    opp_p = d4(ox, oy, px, py)
    do_intercept = opp_p + 1 < my_p

    primary_dx, primary_dy = step_toward(sx, sy, tx, ty)
    alt_dx, alt_dy = step_toward(sx, sy, px, py)

    def score_move(nx, ny):
        # Primary objective: reduce distance to our chosen target.
        s = d4(nx, ny, tx, ty)
        # If intercept, also reduce distance to pressure target and penalize giving up too much.
        if do_intercept:
            s2 = d4(nx, ny, px, py)
            s = (s, s2)
        # Obstacle-avoid and slight preference to avoid letting opponent close on its next greedy step.
        # Predict opponent next greedy step toward its closest resource.
        opp_best = None
        opp_best_d = None
        for rx, ry in resources:
            od = d4(ox, oy, rx, ry)
            if opp_best_d is None or od < opp_best_d:
                opp_best_d, opp_best = od, (rx, ry)
        rx0, ry0 = opp_best
        odx, ody = step_toward(ox, oy, rx0, ry0)
        next_ox, next_oy = ox + odx, oy + ody
        if 0 <= next_ox < w and 0 <= next_oy < h and (next_ox, next_oy) not in obs:
            # Penalize moves that increase our distance to the resource opponent is likely taking (rx0,ry0)
            s = (s[0] if isinstance(s, tuple) else s, d4(nx, ny, rx0, ry0))
        # Tie-break: prefer closer to center a bit.
        center = abs(nx - cx) + abs(ny - cy)
        if isinstance(s, tuple):
            return (s[0], s[1] if len(s) > 1 else 0, s[2