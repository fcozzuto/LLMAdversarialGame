def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    obs = set((a, b) for a, b in obstacles)

    def sgn(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    # If no resources, drift toward opponent side deterministically
    if not resources:
        dx = sgn(ox - x)
        dy = sgn(oy - y)
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            return [dx, dy]
        # fallback: try staying or single-axis
        cand = [(dx, 0), (0, dy), (0, 0)]
        for cdx, cdy in cand:
            nx, ny = x + cdx, y + cdy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                return [cdx, cdy]
        return [0, 0]

    # Target: nearest resource by Manhattan (tie: farther from opponent to reduce contest)
    best = None
    bx, by = x, y
    for rx, ry in resources:
        d = abs(rx - x) + abs(ry - y)
        oppd = abs(rx - ox) + abs(ry - oy)
        key = (d, -oppd, rx, ry)
        if best is None or key < best:
            best = key
            bx, by = rx, ry

    dx0 = sgn(bx - x)
    dy0 = sgn(by - y)

    # Prefer diagonal; if blocked, try axis steps; otherwise sidestep deterministically
    candidates = []
    candidates.append((dx0, dy0))
    candidates.append((dx0, 0))
    candidates.append((0, dy0))
    # Sidestep options: swap order and minor perturbations
    candidates.append((dx0, -dy0))
    candidates.append((-dx0, dy0))
    candidates.append((-dx0, 0))
    candidates.append((0, -dy0))
    candidates.append((0, 0))

    # Deterministic avoidance: also disfavor moves that increase distance to the nearest resource too much
    def score_move(cdx, cdy):
        nx, ny = x + cdx, y + cdy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            return 10**9
        # main objective: decrease distance to target
        dt_before = abs(bx - x) + abs(by - y)
        dt_after = abs(bx - nx) + abs(by - ny)
        # secondary: avoid moving into adjacency with opponent deterministically
        adj = (abs(ox - nx) <= 1 and abs(oy - ny) <= 1)
        # tertiary: slight preference to reduce max coordinate movement (stability)
        stability = abs(cdx) + abs(cdy)
        return (dt_after - dt_before, 1 if adj else 0, stability, nx, ny)

    best_c = None
    best_val = None
    for cdx, cdy in candidates:
        val = score_move(cdx, cdy)
        if best_val is None or val < best_val:
            best_val = val
            best_c = (cdx, cdy)

    if best_c is None:
        return [0, 0]
    return [int(best_c[0]), int(best_c[1])]