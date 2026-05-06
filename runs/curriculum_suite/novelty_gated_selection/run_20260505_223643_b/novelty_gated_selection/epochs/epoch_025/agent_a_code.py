def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    def cd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev distance (diagonals)

    if not resources:
        return [0, 0]

    # Pick resource where we are relatively ahead; if none, pick one where we reduce opponent's lead most.
    best = None
    for rx, ry in resources:
        ds = cd(sx, sy, rx, ry)
        do = cd(ox, oy, rx, ry)
        lead = do - ds  # positive is good
        # Small penalty for requiring "around" obstacles: discourage targets behind an obstacle column/row near the line
        pen = 0
        ax, ay = sx, sy
        bx, by = rx, ry
        step_x = 0 if bx == ax else (1 if bx > ax else -1)
        step_y = 0 if by == ay else (1 if by > ay else -1)
        cx, cy = ax + step_x, ay + step_y
        if inb(cx, cy) and (cx, cy) in obs:
            pen += 2
        val = (lead, -ds, -(rx + ry), -pen)
        if best is None or val > best[0]:
            best = (val, rx, ry)

    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # If stepping directly into an obstacle-adjacent "trap", choose a safer parallel move.
    nx, ny = sx + dx, sy + dy
    if inb(nx, ny) and (nx, ny) in obs:
        cand = [(dx, dy), (dx, 0), (0, dy), (0, 0), (-dx, dy), (dx, -dy)]
        bestm = None
        for mx, my in cand:
            ax, ay = sx + mx, sy + my
            if not inb(ax, ay) or (ax, ay) in obs:
                continue
            # maximize advantage after the move
            score = 0
            for rx, ry in resources:
                ds2 = cd(ax, ay, rx, ry)
                do2 = cd(ox, oy, rx, ry)
                score = max(score, do2 - ds2)
            mval = (score, -cd(ax, ay, tx, ty))
            if bestm is None or mval > bestm[0]:
                bestm = (mval, mx, my)
        if bestm is not None:
            return [int(bestm[1]), int(bestm[2])]
        return [0, 0]

    return [int(dx), int(dy)]