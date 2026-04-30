def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y) and (x, y) not in obst:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_next(nx, ny):
        if (nx, ny) in obst:
            return (10**9, 10**9, 10**9)
        if not inside(nx, ny):
            return (10**9, 10**9, 10**9)
        if resources:
            best = None
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                adv = d_me - d_op  # lower is better (more negative means we are closer)
                # prefer targets we can reach sooner, but also avoid giving opponent a lead
                key = (adv, d_me, d_op, rx, ry)
                if best is None or key < best:
                    best = key
            # smaller best is better; incorporate staying away from obstacles slightly
            obs_adj = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in obst:
                        obs_adj += 1
            return (best[0], best[1], best[2] + obs_adj * 0.01)
        else:
            # no resources: drift toward the opponent's corner to contest space
            d1 = cheb(nx, ny, ox, oy)
            centerx, centery = (w - 1) // 2, (h - 1) // 2
            d2 = cheb(nx, ny, centerx, centery)
            return (d1, d2, nx + ny * 0.001)

    best_delta = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        key = score_next(nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_delta = (dx, dy)
    return [int(best_delta[0]), int(best_delta[1])]