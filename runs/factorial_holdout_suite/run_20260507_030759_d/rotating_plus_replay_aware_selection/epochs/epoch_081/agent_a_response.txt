def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = abs(bx - ax)
        dy = abs(by - ay)
        return dx if dx > dy else dy
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)  # run slightly away
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    # If we are on a resource, stay (collection is priority).
    if any((sx, sy) == (rx, ry) for rx, ry in resources):
        return [0, 0]

    # Pick target by "race advantage": (opp_time - our_time), then closer-to-us.
    best_r = resources[0]
    best_key = (-10**18, -10**18)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d_own = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        key1 = d_opp - d_own
        key2 = -d_own
        if key1 > best_key[0] or (key1 == best_key[0] and key2 > best_key[1]) or (key1 == best_key[0] and key2 == best_key[1] and (rx + ry) > (best_r[0] + best_r[1])):
            best_key = (key1, key2)
            best_r = (rx, ry)

    tx, ty = best_r
    # Greedy step toward target with obstacle avoidance using lookahead-1 scoring.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        # Primary: reduce distance to target more than it helps opponent
        own_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        # Secondary: avoid stepping into positions worse for racing overall
        v = (opp_d - own_d) * 1000 - own_d
        # Tertiary: move closer to target in manhattan to break ties
        v -= abs(tx - nx) + abs(ty - ny)
        if v > bestv:
            bestv, best = v, (dx, dy)
    return [best[0], best[1]]