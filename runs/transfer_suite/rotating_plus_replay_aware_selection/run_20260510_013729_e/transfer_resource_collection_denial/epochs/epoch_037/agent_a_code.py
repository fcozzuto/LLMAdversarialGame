def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue

        # Look for the resource where, after this move, we are most ahead in "capture closeness".
        # Prefer positive advantage; if none, choose move that least favors the opponent.
        best_adv = None
        best_ds = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # higher is better (we are closer sooner)
            key = (adv, -ds, -(rx * 8 + ry))
            if best_adv is None or key > (best_adv, best_ds, 0):
                best_adv = adv
                best_ds = ds

        # If best_adv positive, go for biggest; else reduce opponent lead (maximize adv, minimize our ds).
        key2 = (best_adv, -best_ds, -(dx * 3 + dy))
        if best_key is None or key2 > best_key:
            best_key = key2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]