def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        # Fallback: avoid obstacles and drift toward center deterministically
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                sc = (abs(nx - cx) + abs(ny - cy), dx, dy)
                if best is None or sc < best[0]:
                    best = (sc, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Pick target resource: maximize (opponent farther than us) advantage
    best_r = None
    best_score = None
    for rx, ry in resources:
        dS = cheb(sx, sy, rx, ry)
        dO = cheb(ox, oy, rx, ry)
        adv = dO - dS
        # Prefer winning races; slight tie-break toward smaller self distance.
        sc = (-adv, dS, rx, ry)
        if best_score is None or sc < best_score:
            best_score = sc
            best_r = (rx, ry)

    rx, ry = best_r

    # Predict opponent next position by same targeting (deterministic)
    opp_best = None
    opp_score = None
    for dx, dy in dirs:
        nx, ny = ox + dx, oy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            sc = (cheb(nx, ny, rx, ry), dx, dy)
            if opp_score is None or sc < opp_score:
                opp_score = sc
                opp_best = (nx, ny)
    opp_next = opp_best if opp_best is not None else (ox, oy)

    # Choose our move minimizing distance to target, avoiding direct interception
    best = None
    best_sc = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            sc = cheb(nx, ny, rx, ry)
            if (nx, ny) == opp_next:
                sc += 2  # avoid stepping into likely capture square
            # Deterministic tie-break
            sc_t = (sc, abs(dx) + abs(dy), dx, dy)
            if best_sc is None or sc_t < best_sc:
                best_sc = sc_t
                best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]