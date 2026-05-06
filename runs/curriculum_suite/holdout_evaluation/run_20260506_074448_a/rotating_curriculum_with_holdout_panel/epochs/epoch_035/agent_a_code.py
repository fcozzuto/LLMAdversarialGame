def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = [0, 0]
    best_score = -10**18

    # Mode selection: if opponent is closer to all resources, focus on interception; else race.
    my_closest = None
    opp_closest = None
    for rx, ry in resources:
        dmy = man(sx, sy, rx, ry)
        dop = man(ox, oy, rx, ry)
        if my_closest is None or dmy < my_closest:
            my_closest = dmy
        if opp_closest is None or dop < opp_closest:
            opp_closest = dop
    intercept_mode = False
    if resources and my_closest is not None and opp_closest is not None:
        intercept_mode = opp_closest <= my_closest

    # Deterministic preference: avoid obstacles; prefer moves that change Manhattan distance as expected.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        if not resources:
            # No resources: drift to center while keeping away from opponent slightly.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            val = -(man(nx, ny, cx, cy)) - 0.01 * man(nx, ny, ox, oy)
            if val > best_score:
                best_score = val
                best = [dx, dy]
            continue

        # Evaluate move by best achievable resource according to steal/intercept heuristic.
        # Score favors resources where (opp_dist - my_dist) is large (steal advantage).
        # Intercept mode additionally penalizes moving away from opponent-chosen region.
        move_best = -10**18
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)

            # If opponent can reach same resource sooner, discourage unless we can beat them by being closer now.
            steal_adv = opd - myd  # positive means we are closer than opponent
            if steal_adv < -2:
                continue

            # Secondary terms: prefer reducing distance to resource, and staying away from obstacles isn't explicitly needed.
            base = steal_adv * 2.5 - myd * 0.25

            if intercept_mode:
                # Estimate opponent "pull" to its nearest resource; penalize moving away from that pull.
                # Deterministically compute opponent nearest resource among current resources.
                # (Cheap: compute once per candidate by selecting minimum man distance.)
                # To keep lines low, approximate using closest distance only:
                # penalize if we increase distance to opponent.
                base -= 0.15 * (man(nx, ny, ox, oy) - man(sx, sy, ox, oy))

            # Small deterministic tie-break: prefer moves closer to center (prevents loops).
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            base -= 0.002 * ((nx - cx) ** 2 + (ny - cy) ** 2)

            if base > move_best:
                move_best = base

        # Also consider that if we can step onto a resource, do it deterministically.
        if (nx, ny) in set(tuple(p) for p in resources):
            move_best = max(move_best, 1000 - man(nx, ny, ox, oy))

        # Penalize staying still if it doesn't improve.
        if dx == 0 and dy == 0:
            move_best -= 0.5

        # Deterministic tie-break: prefer lexicographically smaller (dx,dy) among equals.
        if move_best > best_score or (move_best == best_score and (dx, dy) < tuple(best)):
            best_score = move_best
            best = [dx, dy]

    return [int(best[0]), int(best[1])]