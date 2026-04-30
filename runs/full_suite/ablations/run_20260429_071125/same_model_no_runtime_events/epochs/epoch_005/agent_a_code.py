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
        best = None; bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            v = -cheb(nx, ny, tx, ty)  # deterministic fallback
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Choose a target that we are relatively closer to than the opponent,
    # then move one step towards it (with obstacle check); otherwise fallback to board-eval.
    best_r = None; best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        key1 = (do - ds)  # positive means we are closer
        key2 = ds         # tie-break: smaller distance to us
        key3 = -cheb(ox, oy, rx, ry)  # secondary: make opponent farther
        k = (key1, -ds, key3, rx, ry)
        if best_key is None or k > best_key:
            best_key = k
            best_r = (rx, ry)
    rx, ry = best_r

    # Step towards target with deterministic tie-breaking.
    toward = None
    cx = 0 if rx == sx else (1 if rx > sx else -1)
    cy = 0 if ry == sy else (1 if ry > sy else -1)
    cand = [(cx, cy), (cx, 0), (0, cy), (0, 0), (cx, -cy), (-cx, cy), (-cx, 0), (0, -cy), (-cx, -cy)]
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            toward = (dx, dy); break
    if toward is not None:
        return [toward[0], toward[1]]

    # Fallback evaluation: maximize advantage and local resource density.
    def eval_at(nx, ny):
        myd = 10**9
        opd = 10**9
        cnt = 0
        for rxi, ryi in resources:
            d1 = cheb(nx, ny, rxi, ryi)
            if d1 < myd: myd = d1
            d2 = cheb(ox, oy, rxi, ryi)
            if d2 < opd: opd = d2
            if d1 <= 2: cnt += 1
        return (opd - myd) * 200 + cnt * 50 - myd

    best = (0, 0); bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        v = eval_at(nx, ny)
        if v > bestv:
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]