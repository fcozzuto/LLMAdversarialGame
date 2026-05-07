def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center = ((w - 1) // 2, (h - 1) // 2)

    if not resources:
        tx, ty = center
        best = [0, 0]
        best_key = (-10**18, 10**18)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            key = (-d, d)
            if key > best_key:
                best_key = key
                best = [dx, dy]
        return best

    # Prefer moving to a resource where we arrive sooner than opponent; else block by reducing opponent lead.
    best_move = [0, 0]
    best_key = (-10**18, -10**18, 10**18, 10**18)
    scored_targets = []
    for r in resources:
        rx, ry = r
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        ahead = do - ds  # positive means we closer
        scored_targets.append((ahead, ds, rx, ry))
    # Deterministic ordering for equal keys
    scored_targets.sort(key=lambda t: (-t[0], t[1], t[2], t[3]))

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate against top few closest resources for robustness with small cost.
        move_best = (-10**18, -10**18, 10**18, 10**18)
        for i in range(0, 4):
            ahead, ds0, rx, ry = scored_targets[i]
            ds1 = cheb(nx, ny, rx, ry)
            do1 = cheb(ox, oy, rx, ry)
            my_adv = do1 - ds1
            # Key: maximize advantage; then minimize my distance; then maximize opponent disadvantage; then tie-break by coords.
            key = (my_adv, -ds1, -(do1), rx * 100 + ry)
            if key > move_best:
                move_best = key
        # Use move_best plus slight preference for not staying when tied
        stay_penalty = 1 if (dx == 0 and dy == 0) else 0
        key2 = (move_best[0], move_best[1], -stay_penalty, move_best[2])
        if key2 > best_key:
            best_key = key2
            best_move = [dx, dy]

    return best_move