def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick an "uncontested-or-ours-soon" target: prioritize resources where we can arrive earlier by a good margin.
    best_t = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in blocked:
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive => we are earlier
        # Primary: larger margin; Secondary: smaller our distance; Tertiary: deterministic tie-break by position.
        key = (margin, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        # No valid targets: move to reduce distance to the most reachable resource (deterministic).
        if not resources:
            return [0, 0]
        tx, ty = resources[0]
        best_key = None
        best_move = (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                key = (-cheb(nx, ny, tx, ty), dx, dy)
                if best_key is None or key > best_key:
                    best_key, best_move = key, (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = best_t

    # Choose move that maximizes being earlier on the chosen target, while avoiding getting too close to the opponent.
    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        ds_after = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        margin_after = do - ds_after  # higher is better
        # Penalize moving closer to opponent to reduce their ability to contest next.
        dist_op_after = cheb(nx, ny, ox, oy)
        score = (margin_after, dist_op_after, -ds_after, -dx, -dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]