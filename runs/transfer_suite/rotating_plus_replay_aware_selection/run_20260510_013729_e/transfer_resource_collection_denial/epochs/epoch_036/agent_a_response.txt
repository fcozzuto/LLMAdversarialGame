def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target_after(px, py):
        # Prefer resources where we are closer than opponent; maximize distance advantage.
        best = None
        for rx, ry in resources:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds  # positive => we are closer
            # When equal, prefer nearer resources and deterministic ordering.
            key = (margin, -ds, -(rx * 8 + ry))
            if best is None or key > best:
                best = key
        return best  # tuple

    candidates = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 0), (0, 1),
                  (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            nx, ny = sx, sy  # engine keeps in place if invalid

        tgt = best_target_after(nx, ny)
        margin, neg_ds, neg_id = tgt
        ds = -neg_ds

        # Extra pressure: if we can't be closer, still try to reduce opponent's best margin.
        opp_best = None
        for rx, ry in resources:
            do = cheb(ox, oy, rx, ry)
            ds_now = cheb(nx, ny, rx, ry)
            m = do - ds_now
            key = (m, -ds_now, -(rx * 8 + ry))
            if opp_best is None or key > opp_best:
                opp_best = key
        # opp_best[0] is our margin; smaller is worse for us, so use it inversely.
        score = (margin, -ds, -opp_best[0], neg_id)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]