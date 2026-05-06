def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def cell_in(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def step_blocked(nx, ny):
        return (nx, ny) in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def target_pref(tx, ty, mx, my):
        me_d = abs(tx - mx) + abs(ty - my)
        opp_d = abs(tx - ox) + abs(ty - oy)
        lead = opp_d - me_d  # prefer being closer than opponent
        # If we can reach in same/immediate range, strongly prefer.
        reach_bias = 20 - me_d
        return lead * 1000 + reach_bias * 10 - opp_d * 0.01 - me_d * 0.1

    # Choose a target cell to aim for (deterministically from current position).
    best_t = None
    best_tv = None
    for r in resources:
        tx, ty = r[0], r[1]
        tv = target_pref(tx, ty, x, y)
        if best_tv is None or tv > best_tv:
            best_tv = tv
            best_t = (tx, ty)

    # If we're on the target already, keep going for the best nearby alternative deterministically.
    if best_t == (x, y):
        # pick next-best target by increasing resource index order among ties
        best2_tv = None
        best2_t = None
        for r in resources:
            tx, ty = r[0], r[1]
            if (tx, ty) == (x, y):
                continue
            tv = target_pref(tx, ty, x, y)
            if best2_tv is None or tv > best2_tv:
                best2_tv = tv
                best2_t = (tx, ty)
        if best2_t is None:
            return [0, 0]
        best_t = best2_t

    tx, ty = best_t

    # Evaluate local moves by resulting preference, with obstacle penalty.
    best_move = [0, 0]
    best_score = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not cell_in(nx, ny):
            continue
        if step_blocked(nx, ny):
            continue
        # primary: move to improve target preference
        sc = target_pref(tx, ty, nx, ny)
        # secondary: slightly reduce distance to opponent if we're not ahead (predator pressure)
        my_d = abs(nx - ox) + abs(ny - oy)
        my_self_d = abs(nx - tx) + abs(ny - ty)
        sc += (0.5 if (my_self_d <= 2) else 0.0) - my_d * 0.001 - my_self_d * 0.05
        if best_score is None or sc > best_score:
            best_score = sc
            best_move = [dx, dy]

    # If all moves blocked, stay.
    return best_move if best_move in ([d[0], d[1]] for d in dirs) else [0, 0]