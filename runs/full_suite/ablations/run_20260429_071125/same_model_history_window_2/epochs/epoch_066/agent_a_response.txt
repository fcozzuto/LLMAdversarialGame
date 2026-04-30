def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = (int(sp[0]), int(sp[1])) if isinstance(sp, (list, tuple)) and len(sp) >= 2 else (0, 0)
    ox, oy = (int(op[0]), int(op[1])) if isinstance(op, (list, tuple)) and len(op) >= 2 else (0, 0)

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # pick a few closest resources deterministically
    res_scored = []
    for rx, ry in resources:
        res_scored.append((cheb(sx, sy, rx, ry), rx, ry))
    res_scored.sort(key=lambda t: (t[0], t[1], t[2]))
    targets = res_scored[:4]

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        # aim: progress toward best target, with small bias to avoid being too close to opponent
        best_target_score = -10**18
        for _, rx, ry in targets:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # if opponent is closer to this resource, still allow pursuing but penalize
            lead = d_op - d_me
            # local resource concentration in 1-tile neighborhood
            dens = 0
            for px, py in resources:
                if cheb(nx, ny, px, py) <= 1:
                    dens += 1
            val = (-(d_me)) + 0.35 * lead + 0.08 * dens
            if val > best_target_score:
                best_target_score = val

        # extra safety: keep distance from opponent somewhat
        v = best_target_score + 0.12 * cheb(nx, ny, ox, oy)
        # deterministic tie-break: prefer smaller dx, then smaller dy, then standing still
        if v > bestv:
            bestv = v
            best = (dx, dy)
        elif v == bestv:
            if (dx, dy) < best:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]