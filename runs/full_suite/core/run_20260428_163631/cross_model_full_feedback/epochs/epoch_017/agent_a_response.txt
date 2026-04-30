def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        try:
            x, y = p
            obst.add((int(x), int(y)))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        try:
            x, y = r
            x, y = int(x), int(y)
            if inb(x, y) and (x, y) not in obst:
                res.append((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # If no resources, move to increase distance from opponent while staying safe-ish
    if not res:
        best = None
        bestk = None
        for dx, dy, nx, ny in cand:
            d = cheb(nx, ny, ox, oy)
            # Prefer moves that don't walk into obstacle corners: just keep lexicographic
            k = (d, -cheb(nx, ny, 0, 0), dx, dy)
            if bestk is None or k > bestk:
                bestk, best = k, (dx, dy)
        return [best[0], best[1]]

    best = None
    bestk = None
    # Evaluation: choose move that maximizes advantage to the best target.
    # Advantage for a target t: (opp_dist - my_dist). Larger is better.
    for dx, dy, nx, ny in cand:
        min_my_adj_pen = 0
        od = cheb(nx, ny, ox, oy)
        if od <= 1:
            min_my_adj_pen = 5  # avoid getting too close/easy contest

        # Pick target that gives best advantage; if none, minimize opponent advantage.
        best_adv = None
        best_my_dist = None
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            # Prefer positive-adv targets; tie-break by smaller my distance
            if best_adv is None or adv > best_adv or (adv == best_adv and myd < best_my_dist):
                best_adv = adv
                best_my_dist = myd

        # Combine: primary maximize advantage; secondary minimize my distance (reach sooner)
        # tertiary: keep some spacing from opponent.
        k = (best_adv, -best_my_dist, od, -min_my_adj_pen, dx, dy)
        if bestk is None or k > bestk:
            bestk, best = k, (dx, dy)

    return [int(best[0]), int(best[1])]