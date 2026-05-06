def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    center_x = (w - 1) * 0.5
    center_y = (h - 1) * 0.5
    neigh_obs = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, (0, 0))

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue

        # Obstacle proximity penalty (discourage steering into tight areas)
        prox = 0
        for ddx, ddy in neigh_obs:
            ax, ay = nx + ddx, ny + ddy
            if in_bounds(ax, ay) and (ax, ay) in obstacles:
                prox += 1

        myc = cheb(nx, ny, ox, oy)
        my_center = -((nx - center_x) * (nx - center_x) + (ny - center_y) * (ny - center_y))

        local_best = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)

            # Contest resources: want to be as close as possible vs opponent.
            # Also prefer resources where opponent is currently closer (deny).
            deny = 6 * (opd - myd)
            fast = -myd
            lead = 10 * (opd - myd) if myd <= opd else 3 * (opd - myd)
            # If we are equal, slightly prefer routes that keep opponent farther from that resource next.
            tie = -2 * (cheb(ox, oy, rx, ry) - cheb(ox, oy, rx, ry))

            # Avoid giving opponent immediate capture lanes: if opponent would be at/near the same resource
            # after we step, prioritize interception by maximizing our advantage.
            val = deny + fast + lead + tie

            if val > local_best:
                local_best = val

        # Strong center pressure early/mid; diagonal probe tends to advance along diagonals/lanes.
        # Prefer moves that reduce distance to center and keep a bit of spacing from opponent.
        score = local_best + 0.6 * my_center - 0.15 * myc - 0.9 * prox

        # Deterministic tie-break: prefer smaller dx, then dy (stable ordering)
        if score > best[0]:
            best = (score, (dx, dy))
        elif score == best[0] and (dx, dy) < best[1]:
            best = (score, (dx, dy))

    return [best[1][0], best[1][1]]