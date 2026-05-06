def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def blocked(x, y):
        return (not inb(x, y)) or ((x, y) in obs)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    valid_resources = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                valid_resources.append((x, y))
    if not valid_resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # Choose move that maximizes immediate "intercept advantage" over best reachable resource.
    best_score = -10**18
    best_move = (0, 0)
    # Precompute opp distances to each resource for determinism.
    res_info = []
    for tx, ty in valid_resources:
        res_info.append((tx, ty, man(ox, oy, tx, ty)))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # Prefer resource where we are relatively closer than opponent.
        local_best = -10**18
        for tx, ty, od in res_info:
            sd = man(nx, ny, tx, ty)
            # High when (opponent is farther) is bad; we want we are closer, so opp_dist - self_dist large.
            # Small tie-break: prefer smaller self distance and prefer resources "towards" opponent direction.
            tie = -sd
            # Also give a mild bonus if this move reduces opponent's effective lead compared to our current position.
            cur_self_to = min(10**9, min(man(sx, sy, t2x, t2y) for t2x, t2y in valid_resources))
            local = (od - sd) * 100 + tie
            if local > local_best:
                local_best = local
        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]