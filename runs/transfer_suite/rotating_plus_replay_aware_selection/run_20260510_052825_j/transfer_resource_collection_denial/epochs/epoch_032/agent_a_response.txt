def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        d1 = ax - bx
        if d1 < 0:
            d1 = -d1
        d2 = ay - by
        if d2 < 0:
            d2 = -d2
        return d1 + d2

    tr = observation.get("turns_remaining", 0)
    remaining = observation.get("remaining_resource_count", len(resources))
    few = (tr <= 4) or (remaining <= 3)

    def obstacle_pen(x, y, tx, ty):
        # small deterministic penalty for obstacles near the straight-line midpoint
        mx = (x + tx) // 2
        my = (y + ty) // 2
        pen = 0.0
        for ox1, oy1 in obstacles:
            if abs(ox1 - mx) + abs(oy1 - my) <= 1:
                pen += 1.2
        return pen

    # pick best target using simple distance advantage (resource_denier-friendly)
    best = None
    bestv = -1e18
    for rx, ry in resources:
        if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # primary: deny if opponent is closer; secondary: our speed; endgame: nearest/finish
        margin = od - sd
        v = margin * 10.0 - sd * (1.0 if few else 0.35) + (3.5 if sd <= 1 else 0.0)
        if few:
            v += 2.0 / (1 + sd)
        v -= obstacle_pen(sx, sy, rx, ry)
        if v > bestv or (v == bestv and (sd < (best[2] if best else 1e9))):
            bestv = v
            best = (rx, ry, sd)

    if best is None:
        return [0, 0]
    tx, ty = best[0], best[1]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # choose best legal step among 9 options (including stay), avoid obstacles if possible
    moves = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0), (1 if dx == -1 else -1, 0), (0, 1 if dy == -1 else -1), (-dx, -dy)]
    chosen = None
    chosenv = -1e18
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        v = (od - nd) * 10.0 - nd * (1.0 if few else 0.35) + (2.8 if nd <= 1 else 0.0)
        # slight tie-break to keep moving toward target
        v -= 0.01 * (abs(tx - nx) + abs(ty - ny))
        if v > chosenv:
            chosenv = v
            chosen = (mx, my)

    if chosen is None:
        # fallback: stay (engine will keep us in place if invalid)
        return [0, 0]
    return [int(chosen[0]), int(chosen[1])]