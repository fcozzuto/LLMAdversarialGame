def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def obstacle_risk(x, y):
        if (x, y) in obstacles or not inb(x, y):
            return 10**9
        r = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in obstacles:
                    r += 1
        return r

    # Choose the move that maximizes our advantage to the best reachable resource.
    best_move = (0, 0)
    best_val = -10**18
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        risk = obstacle_risk(nx, ny)
        if risk >= 10**8:
            continue

        # Evaluate after making this move: how good is our closest winning target?
        best_t = -10**18
        for tx, ty in resources:
            if (tx, ty) in obstacles:
                continue
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Want opd - myd large (we're closer). Tie-break for nearer targets and centrality.
            dist_center = abs(tx - cx) + abs(ty - cy)
            val = 2.6 * (opd - myd) - 0.10 * myd - 0.03 * dist_center
            # Mild encouragement to keep approaching the opponent's vicinity (steals contested points).
            val += 0.02 * (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))
            if val > best_t:
                best_t = val

        # Penalize risky motion, but don't block diagonal/advantageous paths.
        total = best_t - 0.35 * risk
        if total > best_val:
            best_val = total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]