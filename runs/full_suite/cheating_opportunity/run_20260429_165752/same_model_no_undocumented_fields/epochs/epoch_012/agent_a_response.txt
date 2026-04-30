def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    obs = set()
    for o in obstacles:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            obs.add((int(o[0]), int(o[1])))

    valids = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs:
                valids.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def step_options(cx, cy):
        opts = []
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                opts.append((dx, dy, nx, ny))
        return opts

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    # If we're somehow on obstacle, escape deterministically.
    if (x, y) in obs:
        for dx, dy, nx, ny in step_options(x, y):
            return [dx, dy]
        return [0, 0]

    # Choose candidate targets: closest few by our current distance.
    if valids:
        targets = sorted(valids, key=lambda r: (cheb(x, y, r[0], r[1]), r[0], r[1]))[:6]
    else:
        targets = []

    # If no resources, drift to center-ish to reduce being trapped.
    if not targets:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in step_options(x, y):
            sc = cheb(nx, ny, cx, cy)
            cand = (sc, nx, ny)
            if best is None or cand < best:
                best = cand
                best_move = [dx, dy]
        return best_move

    best_score = None
    best_move = [0, 0]
    for dx, dy, nx, ny in step_options(x, y):
        # Evaluate best target after this move; score = (opp_dist - our_dist) with small bias for closeness.
        move_best = None
        for tx, ty in targets:
            d_our = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            score = (d_opp - d_our) * 10 - d_our  # larger is better
            cand = (-score, tx, ty)  # deterministic min
            if move_best is None or cand < move_best:
                move_best = cand
        # Primary: maximize score => minimize -score; secondary: prefer moves that reduce our distance to chosen best target.
        final_score = move_best[0]
        tie = (nx, ny, dx, dy)
        cand_final = (final_score, tie)
        if best_score is None or cand_final < best_score:
            best_score = cand_final
            best_move = [dx, dy]

    return best_move