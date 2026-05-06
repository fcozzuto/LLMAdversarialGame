def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def legal(x, y): return inb(x, y) and (x, y) not in obs

    cx, cy = (w - 1) // 2, (h - 1) // 2

    def best_target(px, py):
        if not resources: return None, 0
        best_res = None; best_val = None
        for rx, ry in resources:
            ds = man(px, py, rx, ry)
            do = man(ox, oy, rx, ry)
            # Advantage to reach before opponent; tie-break closer to center
            val = (do - ds) * 10 - ds - (man(rx, ry, cx, cy) * 0.2)
            if best_val is None or val > best_val or (val == best_val and (rx, ry) < best_res):
                best_val = val; best_res = (rx, ry)
        return best_res, best_val

    if not resources:
        best = (0, 0); bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): continue
            v = man(nx, ny, ox, oy) * 3 - man(nx, ny, cx, cy)
            if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0); best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): continue
        # Choose a target based on the position after the move
        (tx, ty), adv = best_target(nx, ny)

        # Evaluate: improve our advantage and reduce opponent advantage
        cur_adv = adv
        next_adv = cur_adv
        if tx is not None:
            ds0 = man(sx, sy, tx, ty); ds1 = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            next_adv = (do - ds1) * 10 - ds1 - (man(tx, ty, cx, cy) * 0.2)
            # If we moved closer to target, reward; else slight penalty
            next_adv += (ds0 - ds1) * 2

        # Additional safety: avoid getting too close to opponent unless it helps target racing
        safety = man(nx, ny, ox, oy)
        score = next_adv + safety * 0.2
        if score < -1e9: score = -1e9
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score; best_move = (dx, dy)

    return [best_move[0], best_move[1]]