def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    obs = observation.get("obstacles") or []
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    pursuer = ("purs" in self_role) or ("tag" in self_role) or ("hunter" in self_role)
    if not pursuer:
        if ("purs" in opp_role) or ("tag" in opp_role) or ("hunter" in opp_role):
            pursuer = False  # keep false for evader-style

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        ddx, ddy = nx - ox, ny - oy
        dist2 = ddx * ddx + ddy * ddy
        candidates.append((dist2, dx, dy, nx, ny))

    if not candidates:
        return [0, 0]

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                res_list.append((rx, ry))
    if not res_list:
        best = min(candidates, key=lambda t: t[0]) if pursuer else max(candidates, key=lambda t: t[0])
        return [best[1], best[2]]

    def best_resource_score(nx, ny):
        best = None
        for rx, ry in res_list:
            d = abs(nx - rx) + abs(ny - ry)
            if best is None or d < best:
                best = d
        return best if best is not None else 10**9

    if pursuer:
        scored = []
        for _, dx, dy, nx, ny in candidates:
            scored.append((best_resource_score(nx, ny), abs(nx - ox) + abs(ny - oy), dx, dy))
        best = min(scored, key=lambda t: (t[0], t[1], t[2], t[3]))
        return [best[2], best[3]]
    else:
        scored = []
        for _, dx, dy, nx, ny in candidates:
            scored.append((-best_resource_score(nx, ny), -(abs(nx - ox) + abs(ny - oy)), dx, dy))
        best = min(scored, key=lambda t: (t[0], t[1], t[2], t[3]))
        return [best[2], best[3]]