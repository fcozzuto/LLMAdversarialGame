def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obs_pen(x, y):
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obs:
                    p += 1
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # With no resources, drift away from opponent unless blocked.
        best = None
        bestv = -10**9
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if blocked(nx, ny):
                continue
            v = king_dist(nx, ny, ox, oy) - 0.7 * obs_pen(nx, ny)
            if v > bestv:
                bestv = v
                best = (mx, my)
        return [best[0], best[1]] if best else [0, 0]

    # Denial-first: if opponent is closer to a resource, consider it a prime target to contest.
    my_best = None
    opp_best = None
    for rx, ry in resources:
        dme = king_dist(sx, sy, rx, ry)
        dome = king_dist(ox, oy, rx, ry)
        if my_best is None or dme < my_best[0]:
            my_best = (dme, rx, ry)
        if opp_best is None or dome < opp_best[0]:
            opp_best = (dome, rx, ry)

    # Choose a target deterministically: prefer contested resources; otherwise go for nearest.
    contested = []
    for rx, ry in resources:
        dme = king_dist(sx, sy, rx, ry)
        dome = king_dist(ox, oy, rx, ry)
        if dome <= dme:  # opponent not farther; likely to arrive first or tie
            contested.append((dome, dme, rx, ry))
    if contested:
        contested.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
        _, _, tx, ty = contested[0]
    else:
        _, tx, ty = my_best

    best = (0, 0)
    bestv = -10**9
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if blocked(nx, ny):
            continue
        d_to_t = king_dist(nx, ny, tx, ty)
        d_opp = king_dist(nx, ny, ox, oy)
        # If we step into/near the target resource, boost; also stay away from opponent.
        v = -d_to_t + 0.35 * d_opp - 0.8 * obs_pen(nx, ny)
        # Slight preference to move if can capture a resource this turn.
        if (nx, ny) in set((r[0], r[1]) for r in resources):
            v += 2.5
        if v > bestv:
            bestv = v
            best = (mx, my)
    return [best[0], best[1]]