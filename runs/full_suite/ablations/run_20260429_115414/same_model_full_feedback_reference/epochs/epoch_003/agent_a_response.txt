def choose_move(observation):
    W = observation["grid_width"]
    H = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    res_set = set((p[0], p[1]) for p in resources)
    obs_set = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Build "threat" mask: resources within 1 move of opponent (can be taken next).
    threat = set()
    for rx, ry in resources:
        if max(abs(ox - rx), abs(oy - ry)) <= 1:
            threat.add((rx, ry))

    best = None
    # Target resource that is NOT threatened if possible; else threatened closest to us after avoiding opponent.
    safe_resources = [r for r in resources if (r[0], r[1]) not in threat]
    target_list = safe_resources if safe_resources else resources

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy

        # Immediate gain
        gain = 0
        if (nx, ny) in res_set:
            gain += 50

        # Anticipate opponent next step best capture potential
        opp_best_capture = 0
        for odx, ody in moves:
            nxo, nyo = ox + odx, oy + ody
            if not inb(nxo, nyo) or (nxo, nyo) in obs_set:
                nxo, nyo = ox, oy
            if (nxo, nyo) in threat:
                opp_best_capture = 1
                break

        # Distance pressure: prefer moving closer to a chosen target list while keeping advantage over opponent
        if target_list:
            # Deterministic tie-breaking by (advantage, my_dist, rx, ry)
            best_target = None
            for rx, ry in target_list:
                myd = dist2(nx, ny, rx, ry)
                opd = dist2(ox, oy, rx, ry)
                adv = opd - myd  # positive means we are closer
                key = (-adv, myd, rx, ry)
                if best_target is None or key < best_target:
                    best_target = key
            # Estimate by the best_target's components
            _, myd, rx, ry = best_target
            dist_score = -myd
        else:
            dist_score = 0

        # Also discourage stepping onto a square that lets opponent capture a non-threatening resource next turn
        extra_threat = 0
        for odx, ody in moves:
            nxo, nyo = ox + odx, oy + ody
            if not inb(nxo, nyo) or (nxo, nyo) in obs_set:
                nxo, nyo = ox, oy
            if (nxo, nyo) in res_set:
                extra_threat -= 5

        # Combine: maximize gain, minimize opponent capture threat, maximize dist_score
        score = gain - (30 if opp_best_capture else 0) + dist_score + extra_threat

        # Deterministic move selection: if equal score, choose smaller dx,dy lexicographically
        key = (-score, dx, dy)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]