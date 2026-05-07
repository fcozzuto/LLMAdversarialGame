def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obs_set.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs_set:
                resources.append((rx, ry))

    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        return [dx, dy]

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Predict opponent's next position toward their nearest resource (simple deterministic model).
    opp_next = (ox, oy)
    best_opp_d = None
    for tx, ty in resources:
        d = kdist(ox, oy, tx, ty)
        if best_opp_d is None or d < best_opp_d:
            best_opp_d = d
            tgt = (tx, ty)
    tx, ty = tgt
    odx = 0 if ox == tx else (1 if tx > ox else -1)
    ody = 0 if oy == ty else (1 if ty > oy else -1)
    nx, ny = ox + odx, oy + ody
    if inb(nx, ny):
        opp_next = (nx, ny)

    # Choose resource maximizing arrival advantage; add a small penalty if it's likely on/near opponent's sweep focus.
    best = None
    bx = by = None
    for rx, ry in resources:
        sd = kdist(sx, sy, rx, ry)
        od = kdist(opp_next[0], opp_next[1], rx, ry)
        advantage = od - sd  # bigger => we likely grab first
        # Sweep-avoidance: if resource is on opponent's near row/col alignment, slightly reduce priority.
        align_pen = 0
        if ry == opp_next[1] or rx == opp_next[0]:
            align_pen = 0.5
        tie_dist = sd
        val = (advantage - align_pen, -tie_dist, -kdist(sx, sy, rx, ry))
        if best is None or val > best:
            best = val
            bx, by = rx, ry

    dx = 0 if sx == bx else (1 if bx > sx else -1)
    dy = 0 if sy == by else (1 if by > sy else -1)
    return [dx, dy]