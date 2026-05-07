def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    resources = observation.get("resources", []) or []
    turns_remaining = observation.get("turns_remaining", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    valid_resources = [(r[0], r[1]) for r in resources if inb(r[0], r[1])]
    if not valid_resources:
        return [0, 0]

    # Immediate grab if adjacent
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        for rx, ry in valid_resources:
            if nx == rx and ny == ry:
                return [dx, dy]

    def md(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    # Choose a move that maximizes advantage for claiming next resource first.
    best = None  # (adv, -selfdist, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Defensive penalty near opponent late-game: avoid feeding them easy path
        near_opp = md(nx, ny, ox, oy)
        opp_pen = 0
        if turns_remaining <= 6:
            opp_pen = -2 if near_opp <= 2 else 0

        local_best = None
        for rx, ry in valid_resources:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            adv = (od - sd) + opp_pen
            key = (adv, -sd)
            if local_best is None or key > local_best:
                local_best = key
        if local_best is None:
            continue
        cand = (local_best[0], local_best[1], dx, dy)
        if best is None or cand > best:
            best = cand

    if best is not None:
        return [best[2], best[3]]

    return [0, 0]