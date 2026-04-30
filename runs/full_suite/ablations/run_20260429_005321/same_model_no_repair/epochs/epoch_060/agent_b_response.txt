def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def safe(x, y):
        if (x, y) in obstacles or not inb(x, y):
            return False
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                if (x + ddx, y + ddy) in obstacles:
                    return False
        return True

    if not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def target_value(x, y):
        best = -10**18
        for tx, ty in resources:
            if (tx, ty) in obstacles:
                continue
            myd = cheb(x, y, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Prefer resources we can reach earlier; otherwise block-like preference.
            rel = opd - myd
            center = -0.15 * (abs(tx - cx) + abs(ty - cy))
            # Small tie-break to reduce oscillation: favor moving toward center when close.
            closeness = -0.03 * (myd)
            val = 10.0 * rel + center + closeness
            if val > best:
                best = val
        return best

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        if not safe(nx, ny):
            continue
        val = target_value(nx, ny)
        # Encourage staying on a line toward best value, discourage needless moves.
        if (nx, ny) != (sx, sy):
            val -= 0.02 * cheb(nx, ny, sx, sy)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]