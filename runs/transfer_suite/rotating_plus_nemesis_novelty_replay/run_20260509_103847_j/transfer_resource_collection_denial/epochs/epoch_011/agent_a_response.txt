def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_step_to(target):
        tx, ty = target
        moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
        opp = (ox, oy)
        best = None
        # Tie-break favors: keep within board, reduce our dist to target most; then reduce opponent dist to target;
        # then reduce distance to opponent overall (helps contest).
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            sd2 = man((nx, ny), (tx, ty))
            od2 = man(opp, (tx, ty))
            key = (sd2, -od2, man((nx, ny), opp), tx, ty, dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    # Predict opponent nearest resource (nearest_resource behavior).
    opp = (ox, oy)
    r_op = None
    best_opp_d = None
    for r in resources:
        d = man(opp, r)
        if best_opp_d is None or d < best_opp_d or (d == best_opp_d and (r[0], r[1]) < (r_op[0], r_op[1])):
            best_opp_d = d
            r_op = r

    d_self_to_r0 = man((sx, sy), r_op)
    # If we can contest opponent's target now or tie, go for it. Otherwise choose resource with max advantage.
    if d_self_to_r0 <= best_opp_d:
        target = r_op
    else:
        best_key = None
        target = resources[0]
        for r in resources:
            sd = man((sx, sy), r)
            od = man(opp, r)
            adv = od - sd  # we want big positive (opponent farther)
            # Also prefer reachable/closer resources to reduce risk.
            key = (-adv, sd, r[0], r[1])
            if best_key is None or key < best_key:
                best_key = key
                target = r

    return best_step_to(target)