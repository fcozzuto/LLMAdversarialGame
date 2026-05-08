def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    if not resources:
        return [0, 0]

    best = None
    for rx, ry in resources:
        dself = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        dopp = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
        key = (-(dopp - dself), dself, rx, ry)  # maximize advantage, then nearer, then deterministic
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    tx, ty = best[1]
    dx = sign(tx - sx)
    dy = sign(ty - sy)

    # Candidate moves: prefer diagonal/straight toward target, then alternatives, then stay
    dirs = []
    for ddx in (dx, 0, -dx):
        for ddy in (dy, 0, -dy):
            if ddx == 0 and ddy == 0:
                continue
            dirs.append((ddx, ddy))
    dirs += [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy)]
    seen = set()
    cand = []
    for ddx, ddy in dirs:
        if (ddx, ddy) in seen:
            continue
        seen.add((ddx, ddy))
        nx, ny = sx + ddx, sy + ddy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            cand.append((ddx, ddy))
    if not cand:
        return [0, 0]

    # If we can reach multiple moves equally, pick one that maximizes next-step advantage
    bestm = None
    for ddx, ddy in cand:
        nx, ny = sx + ddx, sy + ddy
        # If target consumed next, prioritize that; otherwise maximize advantage for chosen target.
        adv = -((rx := tx) - nx) * ((rx) - nx) - ((ry := ty) - ny) * ((ry) - ny)
        opp_d = (tx - ox) * (tx - ox) + (ty - oy) * (ty - oy)
        self_d = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        key = (self_d - opp_d, self_d, nx, ny, ddx, ddy)
        if bestm is None or key < bestm[0]:
            bestm = (key, (ddx, ddy))
    return [int(bestm[1][0]), int(bestm[1][1])]