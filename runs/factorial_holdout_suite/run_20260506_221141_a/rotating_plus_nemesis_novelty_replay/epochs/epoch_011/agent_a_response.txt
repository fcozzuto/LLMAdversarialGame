def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < gw and 0 <= ry < gh and (rx, ry) not in obs:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obs:
            cand.append((dx, dy))

    opp_d_cache = {}
    for rx, ry in resources:
        opp_d_cache[(rx, ry)] = dist(ox, oy, rx, ry)

    # Pick a target resource where we can arrive no later; otherwise pick one that is soonest for opponent,
    # but try to reduce their lead.
    best_target = None
    best_key = None
    for rx, ry in sorted(resources):
        sd = dist(sx, sy, rx, ry)
        od = opp_d_cache[(rx, ry)]
        if sd <= od:
            key = (0, sd, od, rx, ry)  # prioritize ability to win the race
        else:
            key = (1, od, sd, rx, ry)  # otherwise: contest the soonest opponent resource
        if best_key is None or key < best_key:
            best_key, best_target = key, (rx, ry)

    rx, ry = best_target
    base_sd = dist(sx, sy, rx, ry)
    base_od = opp_d_cache[(rx, ry)]

    # For each move, evaluate whether we reduce opponent lead on the target,
    # and if not, reduce our distance to the most threatening nearby resource.
    best_move = (0, 0)
    best_score = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        sd2 = dist(nx, ny, rx, ry)
        od2 = base_od  # opponent position unchanged this turn

        if sd2 <= od2:
            lead_score = 1000 - sd2
        else:
            lead_score = - (sd2 - od2)  # closer to equalizing reduces penalty

        # Secondary pressure: nearest resource to opponent
        threat = None
        threat_key = None
        for tr in resources:
            tx, ty = tr
            odt = opp_d_cache[tr]
            if threat_key is None or (odt, dist(nx, ny, tx, ty), tx, ty) < threat_key:
                threat_key = (odt, dist(nx, ny, tx, ty), tx, ty)
                threat = tr
        tx, ty = threat
        sec = -dist(nx, ny, tx, ty)

        # Deterministic ordering
        score = (lead_score, sec, -sd2, dx, dy)
        if best_score is None or score > best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]