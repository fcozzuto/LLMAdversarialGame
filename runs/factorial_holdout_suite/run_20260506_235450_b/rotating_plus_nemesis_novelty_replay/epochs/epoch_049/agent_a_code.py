def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = w - 1, h - 1
        best = (10**9, 10**9)
        bestm = (0, 0)
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            sc = (man(nx, ny, tx, ty), man(nx, ny, ox, oy))
            if sc < best:
                best, bestm = sc, (dx, dy)
        return [bestm[0], bestm[1]]

    # Choose a "winning" resource: where we are closer than opponent; otherwise nearest by advantage.
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer negative (we closer), then smaller ds (faster), then farther from opponent (larger do)
        key = (ds - do, ds, -do)
        if best_key is None or key < best_key:
            best_key, best_r = key, (rx, ry)

    tx, ty = best_r if best_r is not None else (w - 1, h - 1)

    # Move one step to reduce distance while preserving advantage.
    best_score = None
    best_move = (0, 0)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        ns = man(nx, ny, tx, ty)
        no = man(nx, ny, ox, oy)
        # Evaluate advantage at next step: smaller is better
        opp_to = man(ox, oy, tx, ty)
        adv = ns - opp_to
        # Tie-break: closer to target, then safer (farther from opponent), then stay put slightly penalized
        score = (adv, ns, -no, abs(dx) + abs(dy))
        if best_score is None or score < best_score:
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]