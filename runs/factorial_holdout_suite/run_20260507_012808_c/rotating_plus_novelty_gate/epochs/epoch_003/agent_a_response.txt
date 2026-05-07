def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b, c, d):
        ax = a - c
        if ax < 0: ax = -ax
        ay = b - d
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If no resources, drift toward opponent's row/col to contest sweep; avoid obstacles
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs_set:
                # Prefer matching opponent row, then column
                row_term = 0 if ny == oy else cheb(ny, 0, oy, 0)
                col_term = 0 if nx == ox else cheb(nx, 0, ox, 0)
                key = (row_term, col_term, dx, dy)
                if best is None or key < best[0]:
                    best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    # Pick target resource that we can reach earlier and that is also less "aligned" with opponent's sweep
    # (discount resources on opponent's current row to reduce competition with row-sweeping).
    best_target = None
    best_key = None
    for rx, ry in resources:
        self_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Larger advantage is better
        advantage = opp_d - self_d
        # Encourage targeting not on opponent row to avoid giving them a free line
        row_pen = 0 if ry != oy else 3
        key = (-advantage, self_d + row_pen, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target

    # Choose safe move that maximizes immediate improvement toward target while keeping away from obstacles
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d = cheb(nx, ny, tx, ty)
        # Obstacle proximity penalty (stay away from nearby blocks deterministically)
        prox = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                ax = nx + adx
                ay = ny + ady
                if inb(ax, ay) and (ax, ay) in obs_set:
                    prox += 1
        # Also discourage stepping onto cells that are "too close" to opponent in target direction
        opp_d = cheb(ox, oy, tx, ty)
        opp_now = cheb(ox, oy, nx, ny)
        key = (d, prox, opp_d, opp_now, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best else [0, 0]