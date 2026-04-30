def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Evaluate each move by "contested lead" on the best resource after the move.
    # Primary: gain in opponent-vs-me distance for the best resource.
    # Secondary: pick moves that reduce my distance to any resource.
    # Tertiary: avoid getting closer to the opponent (soft blocking).
    best = None
    best_score = None
    res_set = set(resources)

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if not resources:
            # No visible resources: move toward center while staying safe.
            cx, cy = w // 2, h // 2
            myd = cheb(nx, ny, cx, cy)
            opd = cheb(nx, ny, ox, oy)
            score = (-myd, opd)
        else:
            my_best = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Higher is better: opponent farther / me closer for the same resource.
                val = (opd - myd, -myd)
                if my_best is None or val > my_best:
                    my_best = val
            # Bonus if we land directly on a resource (likely immediate pickup).
            bonus = 1 if (nx, ny) in res_set else 0
            # Soft anti-close: slightly prefer not stepping into opponent's immediate range.
            # Range measured by Chebyshev distance.
            opp_close = cheb(nx, ny, ox, oy)
            score = (my_best[0] + bonus * 2, my_best[1], -opp_close, dx, dy)

        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]