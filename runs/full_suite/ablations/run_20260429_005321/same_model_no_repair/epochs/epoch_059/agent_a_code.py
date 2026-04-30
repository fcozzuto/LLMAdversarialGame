def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def safe_cell(x, y):
        if (x, y) in obstacles:
            return False
        # avoid stepping next to obstacles (any 8-neighborhood)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    return False
        return True

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        if not safe_cell(nx, ny):
            continue

        # Evaluate next-step by best resource we could contest from (nx,ny)
        step_val = -10**18
        for tx, ty in resources:
            if (tx, ty) in obstacles:
                continue
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            advantage = opd - myd  # positive => we are closer
            center = -0.06 * (((tx - cx) * (tx - cx)) + ((ty - cy) * (ty - cy)))
            # If opponent is much closer, still try to contest but prefer reducing their lead
            val = 3.2 * advantage - 0.45 * myd + center
            if val > step_val:
                step_val = val
        if step_val > best_val:
            best_val = step_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]