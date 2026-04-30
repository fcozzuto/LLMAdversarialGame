def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Precompute opponent distances to resources (static for this turn).
    opp_d = {}
    for rx, ry in resources:
        opp_d[(rx, ry)] = man(ox, oy, rx, ry)

    def obstacle_proximity(x, y):
        # Higher when safer; keeps movement from hugging obstacles.
        md = 99
        for ax, ay in obstacles:
            d = abs(ax - x) + abs(ay - y)
            if d < md:
                md = d
        if md == 99:
            return 5
        return md

    best_mv = (0, 0)
    best_sc = -10**9

    # New policy: pick the move that creates the largest distance advantage over opponent
    # for the single best resource (advantage-based competition), plus safety bias.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_best = -10**9
        for rx, ry in resources:
            dme = man(nx, ny, rx, ry)
            da = opp_d[(rx, ry)] - dme  # positive => we can arrive sooner/tie
            # Encourage shorter arrival when advantage is similar; discourage losing races strongly.
            sc = 4 * da - dme + 0.15 * (rx + ry)  # deterministic tie bias
            if sc > my_best:
                my_best = sc
        sc_total = my_best + 0.05 * obstacle_proximity(nx, ny) - 0.01 * man(nx, ny, ox, oy)
        if sc_total > best_sc:
            best_sc = sc_total
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]