def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    cx, cy = w // 2, h // 2

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_ok(x, y):
        return inside(x, y) and (x, y) not in obstacles

    if not resources:
        tx, ty = cx, cy
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if step_ok(nx, ny):
            return [dx, dy]
        # deterministic fallback: try axis moves, then stay
        for ddx, ddy in ((dx, 0), (0, dy), (-dx, 0), (0, -dy), (0, 0)):
            nx, ny = sx + ddx, sy + ddy
            if step_ok(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    best = None
    best_score = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Score: prefer being earlier; still prefer nearer if both are later/close.
        lead = do - ds  # positive => we get it not later than opponent
        own_center = cheb(rx, ry, cx, cy)
        # Big weight to lead to win contests; moderate penalty for long routes and being "stuck" near far center.
        score = lead * 100 - ds * 3 - own_center
        # Tie-break deterministically by coordinates
        key = (-(lead), ds, own_center, rx, ry)
        if best is None or score > best_score or (score == best_score and key < best):
            best = key
            best_score = score
            tx, ty = rx, ry

    dx = 0 if sx == tx else (1 if tx > sx else -1)
    dy = 0 if sy == ty else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (0, 0)]
    best_move = (0, 0)
    best_mscore = None
    for ddx, ddy in candidates:
        nx, ny = sx + ddx, sy + ddy
        if not step_ok(nx, ny):
            continue
        # Evaluate immediate improvement towards chosen target, but avoid allowing opponent to flip the contest.
        ds_next = cheb(nx, ny, tx, ty)
        do_curr = cheb(ox, oy, tx, ty)
        mscore = (do_curr - ds_next) * 100 - ds_next
        tieb = (abs(ddx) + abs(ddy), ddx, ddy)
        if best_mscore is None or mscore > best_mscore or (mscore == best_mscore and tieb < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1])):
            best_mscore = mscore
            best_move = (ddx, ddy)

    return [int(best_move[0]), int(best_move[1])]