def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = {(x, y) for x, y in obstacles}
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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_value(x, y):
        # Prefer cells that move us toward resources we can beat opponent on.
        best = None
        for rx, ry in resources:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            diff = do - ds  # positive means we are closer (or tie)
            # tiebreak: smaller ds, then smaller coordinates.
            key = (diff, -ds, -(rx * 8 + ry))
            if best is None or key > best:
                best = key
        return best[0] if best is not None else 0, best[1] if best is not None else 0

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_key = None

    # Base policy: if we can capture something sooner, pursue it; otherwise, go to the best contested/denial target.
    # One-step evaluation for determinism and adaptation.
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        # If we step onto a resource, prioritize heavily.
        on_res = (nx, ny) in {(x, y) for x, y in resources}
        diff_score, neg_ds = cell_value(nx, ny)
        # Also lightly penalize moving away from current best target (use current position evaluation).
        cur_diff, cur_neg_ds = cell_value(sx, sy)
        progress = (diff_score - cur_diff, neg_ds - cur_neg_ds)
        key = (1 if on_res else 0, diff_score, progress[0], progress[1], -(nx * 8 + ny), -(dx * 3 + dy))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]