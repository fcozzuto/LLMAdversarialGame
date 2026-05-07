def choose_move(observation):
    def to_xy(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        return 0, 0

    sx, sy = to_xy(observation.get("self_position"))
    ox, oy = to_xy(observation.get("opponent_position"))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh:
            obstacles.add((x, y))

    resources = []
    for it in observation.get("resources") or []:
        x, y = to_xy(it)
        if 0 <= x < gw and 0 <= y < gh and (x, y) not in obstacles:
            resources.append((x, y))
    if not resources:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    # Predict opponent greedy target (nearest by Manhattan).
    opp_target = min(resources, key=lambda r: (manh(ox, oy, r[0], r[1]), r[0], r[1]))
    opp_td = manh(ox, oy, opp_target[0], opp_target[1])

    # Choose resource with best timing edge vs opponent; break ties deterministically.
    best = None
    best_key = None
    for r in resources:
        sd = manh(sx, sy, r[0], r[1])
        od = manh(ox, oy, r[0], r[1])
        edge = od - sd  # positive means we get there earlier
        # Also slightly prefer resources that are not worse than opponent's nearest by too much.
        # Key: (higher edge, then smaller sd, then lex)
        key = (edge, (opp_td - od), -sd, -r[0], -r[1])
        if best_key is None or key > best_key:
            best_key = key
            best = r

    tx, ty = best

    def step_toward(x, y, tx, ty):
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        # Try diagonal first; if blocked, try single-axis alternatives; else stay.
        cand = [(dx, dy), (dx, 0), (0, dy), (0, 0)]
        for ddx, ddy in cand:
            nx, ny = x + ddx, y + ddy
            if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                return ddx, ddy
        return 0, 0

    ddx, ddy = step_toward(sx, sy, tx, ty)
    return [int(ddx), int(ddy)]