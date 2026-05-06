def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    margin = 0  # be strict to avoid losing races

    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd  # positive means we're sooner
        # Prefer sure-ish grabs; if tied, closer to finish.
        # If we can't win, start denying: go to the resource with smallest od.
        if adv >= margin:
            key = (0, -adv, sd, rx, ry)
        else:
            key = (1, od, sd, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry, sd, od)

    _, tx, ty, _, _ = best

    # Move one step toward target; if blocked, choose best alternative.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    target_dx = 0 if tx == sx else (1 if tx > sx else -1)
    target_dy = 0 if ty == sy else (1 if ty > sy else -1)
    preferred = (target_dx, target_dy)

    best_step = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = md(nx, ny, tx, ty)
        opp_dist = md(nx, ny, ox, oy)
        # prefer reducing distance to target; tie-break: also slightly increase separation from opponent
        key = (dist, -opp_dist, 0 if (dx, dy) == preferred else 1, nx, ny)
        if best_step is None or key < best_step[0]:
            best_step = (key, dx, dy)

    if best_step is None:
        return [0, 0]
    return [int(best_step[1]), int(best_step[2])]