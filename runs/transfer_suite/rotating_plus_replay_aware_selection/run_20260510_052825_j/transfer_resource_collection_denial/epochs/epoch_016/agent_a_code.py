def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0:
            ax = -ax
        if ay < 0:
            ay = -ay
        return ax + ay

    res = []
    for r in resources:
        x, y = r[0], r[1]
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            res.append((x, y))
    if not res:
        return [0, 0]

    best = None
    low_left = observation.get("remaining_resource_count", len(res))
    for rx, ry in res:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd  # prefer targets where opponent is farther
        # when few resources remain, greed harder toward closest available
        if low_left <= 3:
            adv = (od - sd) * 0.5 - sd
        # mild penalty if opponent is already aligned and close (likely sweep)
        if abs(rx - ox) <= 1 and ry == oy:
            adv -= 0.7
        if abs(ry - oy) <= 1 and rx == ox:
            adv -= 0.5
        cand = (adv, -sd, rx, ry)
        if best is None or cand > best:
            best = cand
    tx, ty = best[2], best[3]

    def step_toward(px, py):
        dx = 0 if px == tx else (1 if tx > px else -1)
        dy = 0 if py == ty else (1 if ty > py else -1)
        nx, ny = px + dx, py + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        # deterministic fallback: try ordered neighbors by improvement to target
        dirs = []
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = px + ddx, py + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    dirs.append((man(nx, ny, tx, ty), ddx, ddy))
        if not dirs:
            return [0, 0]
        dirs.sort(key=lambda t: (t[0], t[1], t[2]))
        return [dirs[0][1], dirs[0][2]]

    return step_toward(sx, sy)