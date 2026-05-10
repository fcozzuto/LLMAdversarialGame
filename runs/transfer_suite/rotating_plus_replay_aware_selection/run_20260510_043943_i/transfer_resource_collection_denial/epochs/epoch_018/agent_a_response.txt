def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns_remaining = observation.get("turns_remaining", 0)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def blocked(nx, ny):
        return (nx, ny) in obstacles

    def step_towards(tx, ty):
        best = (0, 0)
        best_sc = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            # avoid stepping into cells that are "too close" to opponent when contesting
            d_self = man(nx, ny, tx, ty)
            d_opp = man(nx, ny, ox, oy)
            d_tx = man(nx, ny, tx, ty)
            sc = (d_self, d_tx + 0.15 * d_opp)
            if best_sc is None or sc < best_sc:
                best_sc = sc
                best = (dx, dy)
        return list(best)

    if not resources:
        # Deterministic retreat/hold: maximize distance from opponent with obstacle safety
        best = [0, 0]
        best_sc = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            sc = (-man(nx, ny, ox, oy), nx + ny)
            if best_sc is None or sc > best_sc:
                best_sc = sc
                best = [dx, dy]
        return best

    # Choose resource where we are "more advantaged" than opponent (self_dist - opp_dist minimal),
    # with a slight preference for nearer resources early.
    best_res = None
    best_val = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Lower is better: we want ds <= do, strongly; break ties by smaller ds and then coordinates
        val = (ds - do, ds + 0.01 * (0 if turns_remaining is None else 0) + 0.0001 * (rx + ry))
        if best_val is None or val < best_val:
            best_val = val
            best_res = (rx, ry)

    tx, ty = best_res

    # If opponent is already closer to our chosen target, switch to any resource where we are relatively closer.
    # (Materially different from prior behavior which used opponent-neighbor prediction.)
    my_win_res = None
    my_win_val = None
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # prefer positive advantage: do - ds large, then smaller ds
        val = (-(do - ds), ds, rx, ry)
        if (do - ds) > 0 or my_win_res is None:
            if my_win_val is None or val < my_win_val:
                my_win_val = val
                my_win_res = (rx, ry)
    if my_win_res is not None:
        tx, ty = my_win_res

    return step_towards(tx, ty)