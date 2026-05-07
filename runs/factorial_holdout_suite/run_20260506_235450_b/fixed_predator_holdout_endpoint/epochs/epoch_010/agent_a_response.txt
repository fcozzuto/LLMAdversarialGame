def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Opponent_denier estimate: likely nearest resource to opponent
    best_opp = min(resources, key=lambda r: (dist(ox, oy, r[0], r[1]), dist(sx, sy, r[0], r[1])))
    opp_target_d = dist(ox, oy, best_opp[0], best_opp[1])
    self_to_best = dist(sx, sy, best_opp[0], best_opp[1])

    # Decide: contest if we can arrive no later; otherwise pivot to best "next" we can beat/steal
    if self_to_best <= opp_target_d:
        target = best_opp
    else:
        # prioritize positive margin (opp farther than us); if all negative, still pick least bad margin,
        # and slightly prefer closer resources for faster pickup.
        def key(r):
            sd = dist(sx, sy, r[0], r[1])
            od = dist(ox, oy, r[0], r[1])
            margin = od - sd  # positive => we are closer
            return (margin, -sd)
        target = max(resources, key=key)

    tx, ty = target
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist(nx, ny, tx, ty)
        # tie-break: if contesting, also keep opponent distance to target large
        od = dist(ox, oy, tx, ty)
        k = (-(nd), -(od), -dist(nx, ny, best_opp[0], best_opp[1]))
        if best_key is None or k > best_key:
            best_key = k
            best = [dx, dy]
    return best