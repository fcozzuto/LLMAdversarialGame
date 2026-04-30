def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, cx, cy)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Contested-resource scoring: minimize (my_dist - op_dist) and also avoid getting too close to opponent.
    best_move = (10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        dmy_opp = cheb(nx, ny, ox, oy)
        # Penalize moving into/near immediate opponent reach.
        opp_pen = 0
        if dmy_opp <= 1:
            opp_pen = 1000
        elif dmy_opp <= 2:
            opp_pen = 200

        best_target = 10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we are relatively closer than opponent.
            contested = myd - opd
            # Also gently prefer shorter actual distance to avoid aimless movement.
            val = contested * 10 + myd
            if val < best_target:
                best_target = val
        score = best_target + opp_pen

        # Tie-break deterministically by dx,dy ordering already stable; use score only.
        if score < best_move[0]:
            best_move = (score, dx, dy)

    return [best_move[1], best_move[2]]