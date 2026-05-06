def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx0 = (w - 1) / 2.0
    cy0 = (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def center_score(x, y):
        dx = x - cx0
        dy = y - cy0
        return -(dx * dx + dy * dy)

    # If there are resources: prefer moves that get closer, especially to resources opponent can't reach first.
    if resources:
        bestv = -10**18
        best = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or not ok(nx, ny):
                continue
            my_best = 10**9
            opp_best = 10**9
            steal_bonus = 0
            for rx, ry in resources:
                myd = man(nx, ny, rx, ry)
                opd = man(ox, oy, rx, ry)
                if myd < my_best:
                    my_best = myd
                if opd < opp_best:
                    opp_best = opd
                # Bonus for resources where we are strictly closer (or can tie-break).
                if myd <= opd:
                    # Stronger bonus when lead is larger and when resource is close.
                    lead = opd - myd
                    steal_bonus = max(steal_bonus, 50 * (lead + 1) - 3 * myd)
            # Penalize being too close to opponent (avoid congestion).
            opp_congestion = -3 * man(nx, ny, ox, oy)
            v = -my_best + 0.15 * opp_best + steal_bonus + 0.05 * center_score(nx, ny) + 0.02 * opp_congestion
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # No resources: move to center while keeping distance from opponent.
    bestv = -10**18
    best = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or not ok(nx, ny):
            continue
        v = 0.6 * center_score(nx, ny) + 0.02 * man(nx, ny, ox, oy)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]