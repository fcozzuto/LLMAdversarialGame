def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    sr = (observation.get("self_role") or "").lower()
    pr = (observation.get("opponent_role") or "").lower()
    purs = ("purs" in sr) or ("catch" in sr) or ("hunt" in sr) or ("chaser" in sr) or ("pursuer" in sr)
    if not purs and ("purs" in pr) or ("catch" in pr) or ("hunt" in pr) or ("chaser" in pr) or ("pursuer" in pr):
        purs = False
    evad = not purs

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    moves = [(dx, dy) for dx in dxs for dy in dys if not (dx == 0 and dy == 0)] + [(0, 0)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        val = -dist2 if purs else dist2
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [best[0], best[1]]