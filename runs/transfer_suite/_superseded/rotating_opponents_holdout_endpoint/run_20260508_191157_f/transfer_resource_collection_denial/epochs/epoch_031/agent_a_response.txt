def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((x, y) for x, y in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Choose target that maximizes potential lead (opponent further than us), with tie favoring nearer.
    best_t = None
    best_lead = -10**18
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        lead = (opd - myd) * 1000 - myd
        if myd == 0:
            lead += 10**9
        # If opponent is very close to the resource, de-prioritize.
        if opd <= 1 and myd > 1:
            lead -= 700
        # Prefer resources that are less blocked by obstacles in a crude way.
        # (Count how many adjacent obstacle cells to the target.)
        adj_obs = 0
        for dx, dy in moves:
            tx, ty = rx + dx, ry + dy
            if inb(tx, ty) and (tx, ty) in obstacles:
                adj_obs += 1
        lead -= adj_obs * 25
        if lead > best_lead:
            best_lead = lead
            best_t = (rx, ry)

    tx, ty = best_t

    # Evaluate one-step moves locally: maximize resulting lead and discourage moving near opponent if it doesn't advance.
    best_m = [0, 0]
    best_s = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        myd2 = man(nx, ny, tx, ty)
        opd2 = man(ox, oy, tx, ty)
        # Primary: increase our advantage in reaching target.
        s = (opd2 - myd2) * 1000 - myd2

        # Secondary: don't let opponent quickly steal our next-best resource.
        # Approximate by checking if opponent is significantly closer to any resource than we are after our move.
        # Limit cost by using only a few closest resources to us.
        if len(resources) <= 6:
            sample = resources
        else:
            # deterministic selection: pick 6 resources with smallest man distance to our current pos
            sample = sorted(resources, key=lambda p: man(sx, sy, p[0], p[1]))[:6]
        steal_risk = 0
        for rx, ry in sample:
            if (rx, ry) in obstacles:
                continue
            mydr = man(nx, ny, rx, ry)
            opdr = man(ox, oy, rx, ry)
            # risk if opponent is already closer, or about to be closer.
            if opdr <= mydr:
                steal_risk += (mydr - opdr + 1)
        s -= steal_risk * 60

        # If opponent is extremely close, prioritize moving to increase distance (to avoid sweep stealing).
        odist = man(nx, ny, ox, oy)
        if odist <= 2:
            s += odist * 40

        # Prefer diagonal progress toward target.
        prog = (abs(nx - tx) + abs(ny - ty))
        s -= prog * 2

        if s > best_s:
            best_s = s
            best_m = [dx, dy]

    return best_m