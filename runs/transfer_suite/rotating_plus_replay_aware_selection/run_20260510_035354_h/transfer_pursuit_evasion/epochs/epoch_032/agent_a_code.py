def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    evade = ("evad" in role) or ("evad" in opp_role and "purs" not in role)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def score_evade(nx, ny):
        md = abs(nx - ox) + abs(ny - oy)
        cheb = max(abs(nx - ox), abs(ny - oy))
        sgnx = 1 if nx > ox else (-1 if nx < ox else 0)
        sgny = 1 if ny > oy else (-1 if ny < oy else 0)
        away = (1 if sgnx == (1 if sx > ox else (-1 if sx < ox else 0)) else 0) + (1 if sgny == (1 if sy > oy else (-1 if sy < oy else 0)) else 0)
        close_obs = 0
        for ax, ay in obs:
            if abs(nx - ax) + abs(ny - ay) == 1:
                close_obs += 1
        center_bias = abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)
        # Prefer corners once distance is comparable to avoid getting herded.
        corner_dist = min(nx + ny, (w - 1 - nx) + ny, nx + (h - 1 - ny), (w - 1 - nx) + (h - 1 - ny))
        return (md, cheb, away, -close_obs, -corner_dist, -center_bias)

    def score_pursue(nx, ny):
        md = abs(nx - ox) + abs(ny - oy)
        cheb = max(abs(nx - ox), abs(ny - oy))
        # Prefer moves that move toward matching both coordinates (diagonal pressure).
        dxdir = 0 if nx == sx else (1 if nx > sx else -1)
        dydir = 0 if ny == sy else (1 if ny > sy else -1)
        toward = 0
        if (ox - nx == 0) or (dxdir == 0):
            toward += 0
        if (oy - ny == 0) or (dydir == 0):
            toward += 0
        close_obs = 0
        for ax, ay in obs:
            if abs(nx - ax) + abs(ny - ay) == 1:
                close_obs += 1
        return (-md, cheb, toward, -close_obs, nx * 0 + ny * 0)

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        if evade:
            key = score_evade(nx, ny)
        else:
            key = score_pursue(nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]