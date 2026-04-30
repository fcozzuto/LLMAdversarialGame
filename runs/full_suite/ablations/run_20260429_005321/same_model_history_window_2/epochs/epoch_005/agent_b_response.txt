def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best_s = -10**18
        tx, ty = w // 2, h // 2
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            sc = (od - sd)  # prefer resources we can reach sooner than opponent
            # small tie-break: prefer closer targets overall
            sc += 0.01 * (-(sd + od))
            if sc > best_s:
                best_s = sc
                tx, ty = rx, ry

    # If opponent is already very close, don't chase only: add mild contesting
    contest = 0.0
    if cheb(sx, sy, ox, oy) <= 2:
        contest = 0.6

    best = [0, 0]
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = md(nx, ny, tx, ty)
        opd = md(ox, oy, tx, ty)
        center_bias = -0.01 * md(nx, ny, w // 2, h // 2)
        contest_bias = contest * (md(nx, ny, ox, oy) * -1.0)  # reduce distance to opponent
        sc = (opd - myd) + center_bias + contest_bias
        if sc > best_sc:
            best_sc = sc
            best = [dx, dy]

    return best