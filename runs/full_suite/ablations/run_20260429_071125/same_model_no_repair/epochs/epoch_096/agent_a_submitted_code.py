def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Predict opponent's likely target: their nearest resource by Chebyshev distance
    opp_nearest = None
    best_od = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        if best_od is None or d < best_od or (d == best_od and (rx, ry) < opp_nearest):
            best_od = d
            opp_nearest = (rx, ry)
    tx, ty = opp_nearest
    stepx = 0 if tx == ox else (1 if tx > ox else -1)
    stepy = 0 if ty == oy else (1 if ty > oy else -1)
    opp_dir = (stepx, stepy)

    def move_delta_towards(px, py, rx, ry):
        dx = 0 if rx == px else (1 if rx > px else -1)
        dy = 0 if ry == py else (1 if ry > py else -1)
        return dx, dy

    # Choose a resource that we can likely secure while not being directly adjacent to opponent pursuit
    opp_dx, opp_dy = opp_dir
    best = None
    best_val = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Score: prefer winning races (opd - myd), and resources far from opponent
        # Add a pursuit penalty if opponent's next step would move closer to that resource.
        if myd == 0:
            val = 10**9
        else:
            nxo, ny o = ox + opp_dx, oy + opp_dy  # might be out of bounds; only used in penalty
            # compute potential closeness after opponent step (Chebyshev, clamped by bounds check)
            if 0 <= nxo < w and 0 <= ny o < h and (nxo, ny o) not in obstacles:
                opd_next = cheb(nxo, ny o, rx, ry)
                pursuit_pen = 0.7 if opd_next < opd else 0.0
            else:
                pursuit_pen = 0.0
            val = (opd - myd) * 2.0 + (opd * 0.15) - (myd * 0.05) - pursuit_pen * (1.0 + 0.01 * (rx + ry))
        if best_val is None or val > best_val or (val == best_val and (rx, ry) < best):
            best_val = val
            best = (rx, ry)

    tr, tc = best
    dx, dy = move_delta_towards(sx, sy, tr, tc)

    # If blocked, try alternative deltas in a deterministic order around the target direction
    candidates = []
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            if a == 0 and b == 0:
                candidates.append((a, b))
            else:
                candidates.append((a, b))
    # Deterministic ordering: prefer deltas that reduce our distance most; avoid obstacles
    best_step = None
    best_step_val