def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev

    best = None
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        score = (do - ds, -ds, rx, ry)
        if best is None or score > best[0]:
            best = (score, (rx, ry))
    tx, ty = best[1]

    dx = 0
    if tx > sx:
        dx = 1
    elif tx < sx:
        dx = -1
    dy = 0
    if ty > sy:
        dy = 1
    elif ty < sy:
        dy = -1

    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                candidates.append((mx, my))
            else:
                candidates.append((mx, my))
    # Prioritize moves that reduce distance to target, then avoid obstacles, then keep deterministic
    cand_scored = []
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        nd = abs(nx - tx)
        nd2 = abs(ny - ty)
        nd_cheb = nd if nd > nd2 else nd2
        # tie-break: prefer diagonal only when it matches target direction
        diag_bonus = 0
        if mx != 0 and my != 0 and ((tx - sx) != 0 and (ty - sy) != 0):
            diag_bonus = 1
        cand_scored.append((( -nd_cheb, -diag_bonus, mx, my), (mx, my)))
    if cand_scored:
        cand_scored.sort(reverse=True)
        return [cand_scored[0][1][0], cand_scored[0][1][1]]

    # If all blocked, stay
    return [0, 0]