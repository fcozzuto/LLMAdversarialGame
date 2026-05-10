def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Infer opponent "nearest_resource" target.
    opp_target = None
    best_od = None
    for rx, ry in resources:
        od = man(ox, oy, rx, ry)
        if best_od is None or od < best_od or (od == best_od and (rx, ry) < opp_target):
            best_od = od
            opp_target = (rx, ry)

    # Choose a resource to get first; if none, choose likely opponent target to intercept.
    target = None
    best_rank = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        reachable_for_me = 1 if myd <= opd else 0
        # Rank: prioritize resources I can reach first; otherwise maximize denial/interception.
        # tie: prefer smaller myd; then larger opponent delay.
        rank = (
            0 if reachable_for_me else 1,
            myd,
            -(opd - myd) if reachable_for_me == 1 else (opd - myd)
        )
        if best_rank is None or rank < best_rank:
            best_rank = rank
            target = (rx, ry)

    # If I can't reach any earlier (likely), bias toward opponent target.
    tx, ty = target
    myd0 = man(sx, sy, tx, ty)
    opd0 = man(ox, oy, tx, ty)
    if myd0 > opd0 and opp_target is not None:
        tx, ty = opp_target

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = man(nx, ny, tx, ty)
        d_opp_t = man(nx, ny, ox, oy)  # small is risky; we want a stable intercept, not to chase opponent
        # Prefer reducing distance to target; tie-break by staying safer relative to opponent.
        val = (d_to_t, d_opp_t, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move