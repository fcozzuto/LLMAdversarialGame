def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Strategic change: if opponent is closer to our nearest resource, pivot to a "swing" resource where we gain the biggest margin.
    if resources:
        nearest_gain = []
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # margin >0 means we are closer
            nearest_gain.append((od - sd, sd, rx, ry))
        # choose best resource by: maximize (we gain margin), then minimize our distance, then prefer upper-left tie-break by coords
        best = None
        best_key = None
        for gain, sd, rx, ry in nearest_gain:
            key = (gain, -sd, -rx, -ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Greedy move selection toward target, while strongly avoiding moving onto/adjacent to obstacles.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # obstacle proximity penalty (encourage paths with free space)
        prox = 0
        for oxr, oyr in obs:
            d = cheb(nx, ny, oxr, oyr)
            if d == 0:
                prox += 10
            elif d == 1:
                prox += 3
            elif d == 2:
                prox += 1
        # relative pressure: also reduce opponent advantage to target after move
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        val = (-myd) + (opd - myd) * 0.6 - prox * 2.0
        # small preference to not drift too much when tied
        val += - (abs(dx) + abs(dy)) * 0.05
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]