def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def obs_cost(x, y):
        if (x, y) in obs_set:
            return 10**9
        if not obstacles:
            return 0
        c = 0
        for ex, ey in obstacles:
            d = man(x, y, ex, ey)
            if d == 0:
                c += 10**6
            elif d == 1:
                c += 80
            elif d == 2:
                c += 25
            elif d == 3:
                c += 10
        return c

    # Choose target deterministically: resources where we have advantage; otherwise closest to us.
    best_targets = []
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        gap = do - ds  # positive => we closer
        best_targets.append((-(gap) if gap < 0 else -gap, ds, rx, ry))
    best_targets.sort()
    # To change policy vs prior behavior: if opponent is much closer to the closest resource, pivot to a resource they are not prioritizing.
    if len(best_targets) > 1:
        _, ds0, tx0, ty0 = best_targets[0]
        _, ds1, tx1, ty1 = best_targets[1]
        if ds0 <= ds1 and man(ox, oy, tx0, ty0) + 1 < man(ox, oy, tx1, ty1):
            target = (tx1, ty1)
        else:
            target = (tx0, ty0)
    else:
        target = (best_targets[0][2], best_targets[0][3])

    tx, ty = target

    # Move scoring: go toward our target, avoid obstacles, and slightly discourage moves that let opponent reach resources sooner.
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= gw or ny >= gh:
            continue
        if (nx, ny) in obs_set:
            continue

        d_self = man(nx, ny, tx, ty)
        # Potential gain: if we step onto any resource, prefer it strongly.
        gain = 0
        for rx, ry in resources:
            if nx == rx and ny == ry:
                gain += 5000 - man(ox, oy, rx, ry)  # prefer uncontested or less contested pickups
        # Opponent pressure: estimate whether opponent could steal a nearby resource.
        pressure = 0
        for rx, ry in resources:
            dn = man(nx, ny, rx, ry)
            dp = man(ox, oy, rx, ry)
            if dn <= 2:
                pressure += max(0, dp - dn) * 1.0
        score = gain - 8 * d_self - obs_cost(nx, ny) - 2.5 * (pressure * 0.01)
        # Tie-break deterministically by move order (already fixed by iteration)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]