def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except:
            pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, run from opponent while staying near center-ish
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy, nx, ny in cand:
            sc = 0.0
            sc += 3.0 * cheb(nx, ny, ox, oy)  # maximize distance from opponent
            sc -= 0.2 * cheb(nx, ny, int(cx), int(cy))
            # prefer forward-ish moves (deterministic minor bias)
            sc += 0.01 * (nx - sx) + 0.005 * (ny - sy)
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Choose best move based on reach to resources and opponent competition
    best = None
    best_res = None
    for dx, dy, nx, ny in cand:
        my_best = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < my_best:
                my_best = d
        # compute penalty for resources where opponent could arrive no later than us
        comp_pen = 0.0
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # if opponent is at least as close, penalize
            if do <= dm:
                # stronger penalty when both are close (tighter race)
                comp_pen += 1.5 / (1.0 + dm)
        # baseline: prefer shorter distance to nearest resource
        sc = -1.8 * my_best - 0.9 * comp_pen
        # also prefer slightly increasing distance from opponent to avoid collisions
        sc += 0.25 * cheb(nx, ny, ox, oy)

        # deterministic tie-breaker: lexicographic by (dx, dy)
        if best is None or sc > best[0] or (sc == best[0] and (dx, dy) < (best[1], best[2])):
            best = (sc, dx, dy)
    return [best[1], best[2]]