def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def local_obst_pen(x, y):
        if (x, y) in occ:
            return -10**18
        pen = 0
        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1),(x+1,y+1),(x+1,y-1),(x-1,y+1),(x-1,y-1)):
            if (nx, ny) in occ:
                pen -= 5
        return pen

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best_s, best_mv = -10**18, (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in occ:
                continue
            s = -cheb(nx, ny, tx, ty) + local_obst_pen(nx, ny)
            if s > best_s or (s == best_s and (dx, dy) < best_mv):
                best_s, best_mv = s, (dx, dy)
        return [best_mv[0], best_mv[1]]

    best_s, best_mv = -10**18, (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in occ:
            continue

        # Choose the single most "swingy" resource from this move, then optimize toward it.
        best_move_score = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Big reward for reducing/closing the race; big reward for actually getting closer.
            swing = opd - myd
            # Tie-break: prefer nearer target and also prefer denying opponent (higher opd).
            s = swing * 1200 + (-myd) * 30 + (opd) * 5
            if s > best_move_score:
                best_move_score = s

        # Additional shaping: prefer not to move into "obstacle-near" zones and keep options.
        # Also lightly discourage going away from the nearest resource.
        near_dist = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        cur_near = min(cheb(sx, sy, rx, ry) for rx, ry in resources)
        progress = cur_near - near_dist  # positive is good
        total = best_move_score + progress * 120 + local_obst_pen(nx, ny)

        if total > best_s or (total == best_s and (dx, dy) < best_mv):
            best_s, best_mv = total, (dx, dy)

    return [best_mv[0], best_mv[1]]