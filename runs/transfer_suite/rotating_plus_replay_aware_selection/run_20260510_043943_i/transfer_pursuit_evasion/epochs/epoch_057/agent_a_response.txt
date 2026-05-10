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

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    is_evader = ("evader" in self_role) or ("evader" in opp_role and "pursuer" not in self_role)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = None

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    corner_targets = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)

        # Obstacle proximity penalty (avoid getting stuck near walls/blocks)
        opn = 0
        for (bx, by) in obstacles:
            dd = cheb(nx, ny, bx, by)
            if dd == 0:
                opn += 999999
            elif dd == 1:
                opn += 8
            elif dd == 2:
                opn += 3

        if is_evader:
            # Flee + drift toward farthest corner from pursuer
            far_corner = 0
            bestc = 0
            for cx, cy in corner_targets:
                dc = cheb(cx, cy, ox, oy)
                if dc > bestc:
                    bestc = dc
                    far_corner = cheb(nx, ny, cx, cy)
            score = (d * 20) + (far_corner * 0.2) - opn
        else:
            # Chase + discourage proximity to obstacles that may block pursuit
            score = (-d * 20) - opn + (1.0 / (1 + cheb(nx, ny, ox, oy)))

        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score

    if best is None:
        return [0, 0]
    return best