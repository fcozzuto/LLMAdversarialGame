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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    res_set = set()
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
                res_set.add((x, y))

    if not res:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_best = 10**9
    for tx, ty in res:
        d = cheb(ox, oy, tx, ty)
        if d < opp_best:
            opp_best = d

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    # Deterministic tie-break order: already fixed by list order.
    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy
        if (nx, ny) not in res_set:
            self_best = 10**9
            cnt2 = 0
            for tx, ty in res:
                d = cheb(nx, ny, tx, ty)
                if d < self_best:
                    self_best = d
                if d <= 2:
                    cnt2 += 1
            if self_best == 10**9:
                self_best = cheb(nx, ny, res[0][0], res[0][1])
            # High weight to getting closer than opponent, plus clustering to reduce travel.
            score = (opp_best - self_best) * 1000 + cnt2 * 25 - cheb(nx, ny, ox, oy)
        else:
            # If on a resource, take immediately; also prefer states that are closer to more resources.
            cnt2 = 0
            for tx, ty in res:
                if cheb(nx, ny, tx, ty) <= 2:
                    cnt2 += 1
            score = 10**12 + cnt2 * 50

        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]