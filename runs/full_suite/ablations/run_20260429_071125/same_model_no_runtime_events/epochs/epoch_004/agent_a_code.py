def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    if not resources:
        tx, ty = 0, 0
        best = (0, 0, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                v = -cheb(nx, ny, tx, ty)
                if v > best[2]:
                    best = (dx, dy, v)
        return [best[0], best[1]]

    # Pick best target: prioritize resources where we are closer than opponent.
    best_rx = best_ry = None
    best_key = (-10**18, 10**18)
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key1 = do - ds  # positive is good
        key2 = ds       # tie-break: smaller ds
        if (key1 > best_key[0]) or (key1 == best_key[0] and key2 < best_key[1]):
            best_key = (key1, key2)
            best_rx, best_ry = rx, ry

    rx, ry = best_rx, best_ry
    ds = cheb(sx, sy, rx, ry)
    do = cheb(ox, oy, rx, ry)
    intercept = (do <= ds)  # opponent is at least as close: try to reduce their access

    best = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nds = cheb(nx, ny, rx, ry)
        if intercept:
            # Maximize reduction of opponent distance compared to ours, and keep ours from getting much worse.
            nod = cheb(nx, ny, ox, oy)
            # Main: deny by moving to squares that still keep us near the target while not letting opponent close too easily.
            opp_next = min(cheb(nx, ny, rx, ry), cheb(nx, ny, rx, ry))  # deterministic placeholder-like identity kept simple
            v = (do - cheb(ox, oy, rx, ry))  # always 0, so rely on secondary terms below
            v = -nds * 3 + (ds - nds) * 2 - nod * 0.3
        else:
            # We are closer: race for the target while keeping some distance from opponent.
            v = (ds - nds) * 4 - cheb(nx, ny, ox, oy) * 0.05
        # Small preference for moving toward (not away from) target to avoid oscillations.
        if v > best[2] or (v == best[2] and (dx, dy) < (best[0], best[1])):
            best = (dx, dy, v)

    return [best[0], best[1]]