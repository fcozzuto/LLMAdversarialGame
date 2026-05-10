def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]
    if (sx, sy) in obstacles:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_sc = -10**9

    # Deterministic tie-break: fixed resource order
    res_order = sorted(resources, key=lambda p: (p[0], p[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Primary: maximize worst-case contest advantage over resources
        # (how much closer we are than the opponent; higher is better)
        worst_adv = 10**9
        best_adv = -10**9
        best_ours = 10**9
        best_opp = 10**9

        for rx, ry in res_order:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive => we are closer than opponent (good)
            if adv < worst_adv:
                worst_adv = adv
            if adv > best_adv:
                best_adv = adv
            if sd < best_ours:
                best_ours = sd
            if od < best_opp:
                best_opp = od

        # Secondary: reduce our distance to the nearest resource we can plausibly win
        nearest_gap = best_opp - best_ours  # if positive, we likely win something soon
        # Tertiary: avoid moving toward being dominated (increase opponent's advantage)
        dom_risk = -worst_adv  # larger when worst_adv is small

        # Combined score (all deterministic, no randomness)
        sc = 5 * worst_adv + 2 * nearest_gap - dom_risk - best_ours

        # Tiny deterministic bias to prevent dithering: prefer smaller dx, then dy, then not moving
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)
        elif sc == best_sc:
            if (abs(dx), abs(dy), dx, dy) < (abs(best[0]), abs(best[1]), best[0], best[1]):
                best = (dx, dy)

    return [best[0], best[1]]