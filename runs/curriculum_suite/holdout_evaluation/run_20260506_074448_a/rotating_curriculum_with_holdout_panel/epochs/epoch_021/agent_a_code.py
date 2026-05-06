def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # Deterministic sweep toward center, prefer reducing both coords distance to center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (abs(nx - cx) + abs(ny - cy), dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    # Choose a resource where we can be earlier than opponent; otherwise contest nearest opponent resource.
    # Also add slight bias to avoid moving away from both resources and opponent.
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        our_d_here = dist((nx, ny), (sx, sy))  # will be 0 or 1 or 2; keep deterministic
        # Evaluate all resources; take best contest advantage
        best_adv = -10**9
        best_opp = 10**9
        best_res_d = 10**9
        for rx, ry in resources:
            r = (rx, ry)
            od = dist((ox, oy), r)
            nd = dist((nx, ny), r)
            adv = od - nd  # positive => we are closer than opponent at this step
            if adv > best_adv or (adv == best_adv and (od < best_opp or (od == best_opp and nd < best_res_d))):
                best_adv = adv
                best_opp = od
                best_res_d = nd
        # Secondary terms: prefer smaller our distance to that target and also keep opponent at distance
        # (safe_collector tends to run for its own targets; we contest or shadow)
        opp_to_move = dist((nx, ny), (ox, oy))
        # Penalty if this move makes us worse relative to the same "best_adv" target (implicit via best_res_d)
        key = (-best_adv, best_res_d, opp_to_move, dx, dy, our_d_here)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move