def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    opp_target = None
    opp_best = None
    for rx, ry in res:
        d = cheb(ox, oy, rx, ry)
        if opp_best is None or d < opp_best or (d == opp_best and (rx, ry) < opp_target):
            opp_best = d
            opp_target = (rx, ry)

    best_move = (0, 0)
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Evaluate by maximum "win margin" after the move (favor chebyshev due to diagonals).
        best_margin = None
        best_self_d = None
        for rx, ry in res:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            margin = opp_d - self_d  # positive means we are sooner
            if best_margin is None or margin > best_margin or (margin == best_margin and self_d < best_self_d):
                best_margin = margin
                best_self_d = self_d

        # If we can't get positive margin, prioritize reducing distance to opponent's nearest target.
        if best_margin is None:
            continue
        if best_margin <= 0 and opp_target is not None:
            rx, ry = opp_target
            opp_near_self_d = cheb(nx, ny, rx, ry)
            key = (best_margin, -opp_near_self_d, best_self_d)
        else:
            key = (best_margin, -best_self_d, best_self_d)

        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]