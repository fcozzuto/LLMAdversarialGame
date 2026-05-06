def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    if not resources:
        # Mirror-pressure: head to the center-ish region opposite the opponent.
        tx = (w - 1) // 2
        ty = (h - 1) // 2
        if ox > (w - 1) / 2:
            tx = (w - 1) // 4
        else:
            tx = (3 * (w - 1)) // 4
        if oy > (h - 1) / 2:
            ty = (h - 1) // 4
        else:
            ty = (3 * (h - 1)) // 4
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = cheb(nx, ny, tx, ty)
            key = (d, cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key < best:
                best = key
        return [best[2], best[3]]

    # Target selection: either contest opponent's nearest resource or take our nearest.
    best_self = None
    best_opp = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        if best_self is None or ds < best_self[0] or (ds == best_self[0] and (rx, ry) < best_self[1]):
            best_self = (ds, (rx, ry))
        do = cheb(ox, oy, rx, ry)
        if best_opp is None or do < best_opp[0] or (do == best_opp[0] and (rx, ry) < best_opp[1]):
            best_opp = (do, (rx, ry))

    our_rx, our_ry = best_self[1]
    op_rx, op_ry = best_opp[1]

    # If we can reach an opponent-nearest resource fast, contest; else pursue our nearest.
    contest = cheb(sx, sy, op_rx, op_ry) <= cheb(sx, sy, our_rx, our_ry) + 1

    tx, ty = (op_rx, op_ry) if contest else (our_rx, our_ry)

    # Scoring per move: reduce our distance; if contesting, also increase opponent's distance to that same target.
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds_next = cheb(nx, ny, tx, ty)
        do_next = cheb(ox, oy, tx, ty)
        # Additional shaping: avoid moving closer to opponent when contesting (to prevent their sweep).
        opp_closeness = cheb(nx, ny, ox, oy)
        key = (ds_next, -do_next if contest else 0, opp_closeness if contest else 0, dx, dy)
        if best is None or key < best:
            best = key
    return [best[3], best[4]]