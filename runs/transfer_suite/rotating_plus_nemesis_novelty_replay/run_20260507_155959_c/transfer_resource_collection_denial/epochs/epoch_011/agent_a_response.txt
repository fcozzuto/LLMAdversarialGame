def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in obs]
    if not res:
        return [0, 0]

    # If immediate pickup possible, take it deterministically.
    res_set = set(res)
    for dx, dy, nx, ny in legal:
        if (nx, ny) in res_set:
            return [dx, dy]

    # Score move by choosing a target resource and maximizing our advantage.
    # Tie-break deterministically by lexicographic move preference.
    best = None
    best_val = None
    for dx, dy, nx, ny in legal:
        min_adv = 10**9
        best_adv_for_target = -10**9
        closest_self = 10**9
        closest_op = 10**9

        for rx, ry in res:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            adv = do - ds  # positive means we are closer than opponent
            if adv < min_adv:
                min_adv = adv
            if adv > best_adv_for_target:
                best_adv_for_target = adv
            if ds < closest_self:
                closest_self = ds
            if do < closest_op:
                closest_op = do

        # Prefer positive advantage; otherwise head to closest resource.
        # Also lightly penalize moves that increase distance to the best target.
        # The weights are fixed for determinism.
        val = 0
        if best_adv_for_target > 0:
            val += 2000 * best_adv_for_target
            val += 50 * (closest_op - closest_self)
        else:
            val += -3 * closest_self
            val += 2 * min_adv  # less bad (closer to some resource than opponent)

        # Tiny deterministic preference: prefer diagonal over straight over stay, then smaller dx/dy.
        diag_pref = 1 if dx != 0 and dy != 0 else 0
        straight_pref = 1 if (dx == 0) != (dy == 0) else 0
        stay_pref = 1 if dx == 0 and dy == 0 else 0
        val += 0.001 * (diag_pref * 3 + straight_pref * 2 + stay_pref * 1)
        key = (-(val), dx, dy)  # maximize val; deterministic tie-break
        if best is None or key < best:
            best = key
            best_val = val

    # Recover chosen move from best key
    _, bx, by = best
    return [bx, by]