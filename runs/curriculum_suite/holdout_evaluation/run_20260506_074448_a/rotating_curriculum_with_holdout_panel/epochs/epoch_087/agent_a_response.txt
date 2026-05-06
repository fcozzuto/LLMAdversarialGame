def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = [(r[0], r[1]) for r in (observation.get("resources") or []) if 0 <= r[0] < w and 0 <= r[1] < h and (r[0], r[1]) not in obstacles]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    # If no resources, head toward center to avoid being edge-controlled.
    if not resources:
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        best = (-10**18, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = -d2(nx, ny, tx, ty)
            if val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    # Target selection: prioritize resources where we are closer than opponent, with some tie-break.
    best_target = None
    best_score = -10**18
    for rx, ry in resources:
        sd = d2(sx, sy, rx, ry)
        od = d2(ox, oy, rx, ry)
        # bonus if we can potentially contest (smaller sd, larger od)
        score = (od - sd) * 10 - sd
        # edge-favoring resources slightly less (edge_patrol tends to grab edges)
        edge = (rx == 0 or ry == 0 or rx == w - 1 or ry == h - 1)
        if edge:
            score -= 15
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    rx, ry = best_target
    # Choose move that maximizes immediate advantage after stepping; deterministic tie-break via ordering.
    best = (-10**18, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd = d2(nx, ny, rx, ry)
        od = d2(ox, oy, rx, ry)
        # also slight deterrent if stepping closer to our opponent (encourages safer approach)
        closeto_opp = d2(nx, ny, ox, oy)
        val = (od - sd) * 10 - sd - (closeto_opp // 8)
        # small preference to progress toward target
        val += -((abs(nx - rx) + abs(ny - ry)) // 2)
        if val > best[0]:
            best = (val, dx, dy)
    return [best[1], best[2]]