def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dsq(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx*dx + dy*dy

    def step_ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        return [0, 0]

    # Choose a strategic target: mostly nearest to self, but if opponent is too close to all,
    # switch to a resource that is far from opponent to avoid being out-raced.
    best_near = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        t = (dsq(sx, sy, rx, ry), dsq(ox, oy, rx, ry), rx, ry)
        if best_near is None or t < best_near[0]:
            best_near = (t, (rx, ry))
    if best_near is None:
        return [0, 0]

    # Determine if opponent has a strong positional edge overall
    best_race_margin = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        self_d = dsq(sx, sy, rx, ry)
        opp_d = dsq(ox, oy, rx, ry)
        margin = self_d - opp_d  # negative => opponent closer
        t = (margin, self_d, opp_d, rx, ry)
        if best_race_margin is None or t < best_race_margin[0]:
            best_race_margin = (t, (rx, ry))
    target = best_near[1]
    # If opponent is closer to the "nearest-to-self" resource by a meaningful amount, invert targeting.
    rx, ry = target
    if dsq(ox, oy, rx, ry) + 1 < dsq(sx, sy, rx, ry):
        best_far_from_opp = None
        for r2x, r2y in resources:
            if (r2x, r2y) in obstacles:
                continue
            opp_d = dsq(ox, oy, r2x, r2y)
            self_d = dsq(sx, sy, r2x, r2y)
            # Prefer far from opponent, but still somewhat reachable by self
            score = (-opp_d, self_d, r2x, r2y)
            if best_far_from_opp is None or score < best_far_from_opp[0]:
                best_far_from_opp = (score, (r2x, r2y))
        if best_far_from_opp is not None:
            target = best_far_from_opp[1]

    tx, ty = target

    # Move selection: greedy toward target with anti-interference term (stay away from opponent),
    # but never consider invalid/obstructed steps.
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue
        d_to_t = dsq(nx, ny, tx, ty)
        d_from_opp = dsq(nx, ny, ox, oy)
        # Primary: reduce distance to target; Secondary: increase distance from opponent.
        # Deterministic tie-break by dx,dy ordering in deltas list.
        val = (d_to_t, -d_from_opp, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move