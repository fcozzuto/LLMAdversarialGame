def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obs
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        best = None
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = (sx + dx), (sy + dy)
            if not free(nx, ny): nx, ny = sx, sy
            v = man(nx, ny, ox, oy)
            if best is None or v > bestv or (v == bestv and (dx, dy) < best):
                best, bestv = (dx, dy), v
        return [best[0], best[1]]

    # Pick resource where we arrive earlier than opponent; otherwise slowest-loss fallback.
    best_r = None
    best_adv = -10**18
    best_ts = 10**18
    for rx, ry in resources:
        ts = man(sx, sy, rx, ry)
        to = man(ox, oy, rx, ry)
        adv = to - ts  # larger means we are faster
        # Strong preference for winning grabs; then race closeness; then deterministic tie-break by coords
        key_adv = adv
        if key_adv > best_adv or (key_adv == best_adv and (ts < best_ts or (ts == best_ts and (rx, ry) < best_r))):
            best_adv, best_ts, best_r = key_adv, ts, (rx, ry)

    rx, ry = best_r

    # Choose a local move that heads toward target while maintaining obstacle safety and race pressure.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        ds = man(nx, ny, rx, ry)
        do = man(ox + 0, oy + 0, rx, ry)  # fixed; used only for relative race term
        # Prefer reducing our distance; also prefer moves that keep us not falling behind.
        score = (best_adv - (ds - best_ts)) * 1000 - ds
        if best_move == (0, 0):
            best_score = score
            best_move = (dx, dy)
        else:
            if score > best_score or (score == best_score and (dx, dy) < best_move):
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]