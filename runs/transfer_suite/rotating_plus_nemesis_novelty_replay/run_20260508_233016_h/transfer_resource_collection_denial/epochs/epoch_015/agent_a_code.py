def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If on a resource, collect.
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    # Opponent pressure: resources it is closest to.
    opp_best_d = None
    opp_best = []
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if opp_best_d is None or d < opp_best_d:
            opp_best_d = d
            opp_best = [(rx, ry)]
        elif d == opp_best_d:
            opp_best.append((rx, ry))
    opp_focus = opp_best[0] if opp_best else resources[0]

    best_move = [0, 0]
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate this move by its ability to secure (or deny) an opponent-focused target,
        # plus overall best advantage on any resource.
        fx, fy = opp_focus
        sd = man(nx, ny, fx, fy)
        od = man(ox, oy, fx, fy)
        focus_adv = od - sd  # higher => we are closer than opponent

        any_adv = None
        any_sd = None
        for rx, ry in resources:
            sd2 = man(nx, ny, rx, ry)
            od2 = man(ox, oy, rx, ry)
            adv2 = od2 - sd2
            if any_adv is None or adv2 > any_adv or (adv2 == any_adv and sd2 < any_sd):
                any_adv = adv2
                any_sd = sd2

        # Prefer moves that create a lead on some resource; if none, reduce opponent's lead.
        # Add slight tie-break: move toward a resource (lower distance).
        lead_term = any_adv if any_adv >= 0 else any_adv * 0.7
        focus_term = focus_adv
        # If we can match/beat the focus target, prioritize it strongly to steal before opponent.
        steal_bonus = 5.0 if focus_adv >= 0 else 0.0
        # Penalize stepping onto/adjacent to obstacles to avoid getting trapped (deterministic).
        adj_pen = 0
        for ox2, oy2 in obstacles:
            if abs(nx - ox2) <= 0 and abs(ny - oy2) <= 0:
                adj_pen += 5
            elif abs(nx - ox2) + abs(ny - oy2) == 1:
                adj_pen += 1

        score = lead_term + 0.6 * focus_term + steal_bonus - 0.2 * any_sd - 0.5 * adj_pen

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move