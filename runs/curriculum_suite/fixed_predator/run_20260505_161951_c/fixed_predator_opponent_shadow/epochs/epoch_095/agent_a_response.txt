def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            key = (md(nx, ny, tx, ty), md(nx, ny, ox, oy))
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # Predict opponent focus: closest resource to opponent
    opp_best_r = None
    opp_best_d = None
    for rx, ry in resources:
        d = md(ox, oy, rx, ry)
        if opp_best_d is None or d < opp_best_d or (d == opp_best_d and (rx, ry) < opp_best_r):
            opp_best_d = d
            opp_best_r = (rx, ry)

    close_threat = md(sx, sy, ox, oy) <= 2

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy

        self_dists = []
        for rx, ry in resources:
            self_dists.append((md(nx, ny, rx, ry), rx, ry))
        self_dists.sort()

        self_min_d, self_rx, self_ry = self_dists[0]
        opp_min_d = md(ox, oy, self_rx, self_ry)

        # Competing metrics
        # If we can beat/tie opponent on their likely target, commit to it strongly.
        target_dx = md(nx, ny, opp_best_r[0], opp_best_r[1])
        target_opp_d = opp_best_d
        beat = target_opp_d - target_dx  # positive if we are closer than opponent after move

        # If threat, also keep distance from opponent while choosing action.
        dist_from_opp = md(nx, ny, ox, oy)

        # Determine if we should "steal" a resource: choose the resource where (opp_d - self_d) is maximal.
        steal_best = None
        for rx, ry in resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            gain = od - sd
            key = (-gain, sd, rx, ry)
            if steal_best is None or key < steal_best[0]:
                steal_best = (key, gain, sd, rx, ry)
        steal_gain = steal_best[1]
        steal_self_d = steal_best[2]

        # Final deterministic key: maximize beat/steal_gain, then minimize our time, then maximize separation if threatened.
        # Use lexicographic ordering with negatives for maximization.
        key = (
            -beat if beat > 0 else 0,              # prefer immediate beating their likely target
            -(steal_gain),                         # prefer best "steal" advantage
            self_min_d,                            # otherwise minimize our nearest resource distance
            -(dist_from_opp if close_threat else 0),  # when threatened, keep farther from opponent
            target_dx,                             # tie-break: closer to their target
            dx, dy
        )

        if best is None or key < best[0]:
            best = (key, (dx, dy))
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]