def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if w <= 0 or h <= 0:
        return [0, 0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy
    def valid_cell(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        # Fallback: keep distance from opponent while moving toward center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = (0, 0, -10**9)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid_cell(nx, ny):
                continue
            sc = -dist((nx, ny), (ox, oy)) - 0.1 * dist((nx, ny), (int(cx), int(cy)))
            if sc > best[2]:
                best = (dx, dy, sc)
        return [best[0], best[1]]

    best_r = resources[0]
    best_adv = -10**9
    for r in resources:
        rd = dist((sx, sy), r)
        od = dist((ox, oy), r)
        adv = od - rd  # positive means we're closer
        # choose resource where we have advantage; if none, choose closest we can reach
        if adv > best_adv or (adv == best_adv and rd < dist((sx, sy), best_r)):
            best_adv = adv
            best_r = r

    # If opponent is clearly closer to all resources, switch to a blocking/interception bias:
    # maximize progress that increases distance to opponent while still moving toward best_r neighborhood.
    intercept = best_adv < 0

    best = (0, 0, -10**18)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid_cell(nx, ny):
            continue
        myd = dist((nx, ny), best_r)
        opd = dist((nx, ny), (ox, oy))
        # favor capturing contested resource; slight defensive component if we are behind
        sc = 0
        sc += -myd
        sc += 0.6 * (dist((sx, sy), best_r) - myd)  # progress this turn
        if intercept:
            sc += 0.2 * opd  # keep away when behind
            sc += 0.1 * (opd - dist((sx, sy), (ox, oy)))
        else:
            sc += -0.15 * opd  # be a bit more assertive
        if sc > best[2]:
            best = (dx, dy, sc)

    return [best[0], best[1]]