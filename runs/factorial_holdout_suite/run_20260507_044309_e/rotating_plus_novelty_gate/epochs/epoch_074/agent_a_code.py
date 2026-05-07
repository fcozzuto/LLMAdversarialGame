def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    for dx, dy, nx, ny in valid:
        if (nx, ny) in res_set:
            return [dx, dy]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2; a = -a if a < 0 else a
        b = y1 - y2; b = -b if b < 0 else b
        return a if a > b else b

    # Score move by best resource it can capture relative to opponent.
    best_move = (0, 0, sx, sy)
    best_score = -10**18
    rc = observation.get("remaining_resource_count", len(resources)) or len(resources)
    for dx, dy, nx, ny in valid:
        # If we just moved onto a resource, it would have been caught above, but keep consistent.
        mv_score = 0
        for rx, ry in resources:
            dme = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Positive when we can reach no later than opponent.
            reach_adv = do - dme
            # Small preference for closer pickup and for reducing "sweep" along opponent's side.
            my_closer = -dme
            # Encourage interception by preferring resources around/near opponent's current row/col alignment.
            sweep = -abs(ry - oy)
            # Late game: prioritize any reachable advantage more strongly.
            late_boost = 1 if observation.get("turns_remaining", 0) is None else 1
            if rc <= 4:
                late_boost = 2
            val = (reach_adv * 6 + my_closer * 1 + sweep * 0.25) * late_boost
            # If reach_adv == 0, still prefer being closer in absolute terms.
            mv_score = max(mv_score, val)
        # If no resources, drift toward center while avoiding obstacles.
        if resources:
            score = mv_score
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            score = -cheb(nx, ny, cx, cy)
        # Deterministic tie-break: prefer smaller |dx|+|dy|, then lexicographic (dx,dy).
        man = abs(dx) + abs(dy)
        cand = (score, -man, -dx, -dy)
        cur = (best_score, - (abs(best_move[0]) + abs(best_move[1])), -best_move[0], -best_move[1])
        if cand > cur:
            best_score = score
            best_move = (dx, dy, nx, ny)

    return [int(best_move[0]), int(best_move[1])]